// Synthetic end-to-end check. Requires installed Node, Chrome and backend/.venv.
// Starts only owned loopback processes and never opens the portfolio database.
import assert from 'node:assert/strict';
import { spawn, execFileSync } from 'node:child_process';
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const python = join(root, 'backend/.venv/bin/python');
const chrome = process.env.MARKETLAB_CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const artifacts = await mkdtemp(join(tmpdir(), 'marketlab-ui-check-'));
const fixture = join(artifacts, 'fixture');
await mkdir(fixture);
const database = join(fixture, 'synthetic.db');
const children = new Set();
let socket;
let server;

function start(command, args, readyPattern, cwd = root) {
    return new Promise((accept, reject) => {
        const process = spawn(command, args, { cwd, stdio: ['ignore', 'pipe', 'pipe'], env: { ...globalThis.process.env, PYTHONDONTWRITEBYTECODE: '1' } });
        children.add(process);
        let output = '';
        const timeout = setTimeout(() => reject(new Error('Owned test process did not become ready.')), 20000);
        const collect = chunk => {
            output += chunk.toString();
            const match = output.match(readyPattern);
            if (match) { clearTimeout(timeout); accept({ process, address: match[1] }); }
        };
        process.stdout.on('data', collect);
        process.stderr.on('data', collect);
        process.on('error', error => { clearTimeout(timeout); reject(error); });
        process.on('exit', code => { clearTimeout(timeout); children.delete(process); reject(new Error(`Owned test process exited (${code}): ${output.slice(-1200)}`)); });
    });
}
async function stop(process) {
    if (process.exitCode !== null) return;
    await new Promise(accept => {
        const force = setTimeout(() => process.kill('SIGKILL'), 5000);
        process.once('exit', () => { clearTimeout(force); accept(); });
        process.kill('SIGTERM');
    });
}
const bootstrap = `
import sys
from pathlib import Path
from database import connection
connection.database_path = Path(sys.argv[1])
from app.main import app
import uvicorn
uvicorn.run(app, host='127.0.0.1', port=0, log_level='info')
`;
async function startBackend() {
    return start(python, ['-B', '-c', bootstrap, database], /Uvicorn running on (http:\/\/127\.0\.0\.1:\d+)/, join(root, 'backend'));
}
let nextId = 0;
const pending = new Map();
function cdp(method, params = {}) {
    const id = ++nextId;
    return new Promise((accept, reject) => {
        const timeout = setTimeout(() => { pending.delete(id); reject(new Error(`Timed out: ${method}`)); }, 15000);
        pending.set(id, { accept, reject, timeout });
        socket.send(JSON.stringify({ id, method, params }));
    });
}
async function evaluate(expression) {
    const result = await cdp('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description || 'Browser evaluation failed.');
    return result.result.value;
}
async function until(expression) {
    const deadline = Date.now() + 10000;
    while (Date.now() < deadline) {
        if (await evaluate(expression)) return;
        await new Promise(accept => setTimeout(accept, 75));
    }
    throw new Error(`Browser condition did not become true: ${expression}`);
}
async function enter(account, ticker, shares) {
    await evaluate(`document.getElementById('account-id').value=${JSON.stringify(account)};
        document.getElementById('ticker').value=${JSON.stringify(ticker)};
        document.getElementById('quantity').value=${JSON.stringify(shares)};
        document.getElementById('opening-form').requestSubmit();`);
    await until(`!document.getElementById('open-holding').disabled`);
}
async function screenshot(name) {
    const { data } = await cdp('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
    const path = join(artifacts, name);
    await writeFile(path, Buffer.from(data, 'base64'));
    console.log(`Screenshot: ${path}`);
}
try {
    execFileSync(python, ['-B', '-c', `
import sqlite3,sys
from pathlib import Path
with sqlite3.connect(sys.argv[1]) as connection:
    connection.executescript(Path(sys.argv[2]).read_text())
    connection.executemany('INSERT INTO accounts(id,name) VALUES (?,?)', [(2,'Synthetic Brokerage'), (7,'Synthetic Retirement')])
`, database, join(root, 'backend/database/schema.sql')]);
    server = await startBackend();
    const browser = await start(chrome, ['--headless=new', '--no-first-run', '--no-default-browser-check', '--disable-background-networking', '--remote-debugging-port=0', `--user-data-dir=${join(fixture, 'chrome-profile')}`, 'about:blank'], /DevTools listening on (ws:\/\/127\.0\.0\.1:\d+\/[^\s]+)/);
    const debugOrigin = browser.address.replace(/^ws:/, 'http:').replace(/\/devtools\/browser\/.*/, '');
    const target = await (await fetch(`${debugOrigin}/json/new?about:blank`, { method: 'PUT' })).json();
    socket = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((accept, reject) => { socket.addEventListener('open', accept, { once: true }); socket.addEventListener('error', reject, { once: true }); });
    socket.addEventListener('message', event => {
        const message = JSON.parse(event.data);
        const callback = pending.get(message.id);
        if (!callback) return;
        pending.delete(message.id);
        clearTimeout(callback.timeout);
        if (message.error) callback.reject(new Error(message.error.message));
        else callback.accept(message.result);
    });
    await cdp('Page.enable');
    await cdp('Runtime.enable');
    await cdp('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1100, deviceScaleFactor: 1, mobile: false });
    await cdp('Page.navigate', { url: server.address });
    await until(`document.getElementById('account-count')?.textContent==='2' && document.getElementById('position-count')?.textContent==='0'`);
    assert.equal(await evaluate(`document.getElementById('account-id').options.length`), 3);
    assert.equal(await evaluate(`document.querySelectorAll('#account-id').length`), 1);
    await evaluate(`document.getElementById('account-id').value='7'; document.getElementById('load-accounts').click()`);
    await until(`!document.getElementById('load-accounts').disabled`);
    assert.equal(await evaluate(`document.getElementById('account-id').value`), '7');
    assert.equal(await evaluate(`document.getElementById('account-id').options.length`), 3);
    await enter('2', 'SYNTHA', '2.25');
    await until(`document.getElementById('position-count').textContent==='1'`);
    await enter('7', 'MICRO', '0.000001');
    await until(`document.getElementById('position-count').textContent==='2'`);
    await enter('2', 'MAXQTY', '9223372036854.775807');
    await until(`document.getElementById('position-count').textContent==='3'`);
    const rows = await evaluate(`Array.from(document.querySelectorAll('#opening-positions-list tr'),row=>Array.from(row.cells,cell=>cell.textContent))`);
    assert.deepEqual(rows, [['SYSYNTHA', 'Synthetic Brokerage', '2.25'], ['MAMAXQTY', 'Synthetic Brokerage', '9223372036854.775807'], ['MIMICRO', 'Synthetic Retirement', '0.000001']]);
    console.log('PASS: page-load accounts; selected IDs; exact submitted quantities through real POST/GET/SQLite.');
    await enter('2', 'SYNTHA', '2.25');
    assert.match(await evaluate(`document.getElementById('open-holdings-list').textContent`), /Error 409/);
    await evaluate(`document.getElementById('account-id').add(new Option('Synthetic missing account','999'))`);
    await enter('999', 'MISSING', '1');
    assert.match(await evaluate(`document.getElementById('open-holdings-list').textContent`), /Error 404/);
    await enter('2', 'INVALID', '0.0000001');
    assert.match(await evaluate(`document.getElementById('open-holdings-list').textContent`), /positive share quantity/);
    await evaluate(`document.getElementById('portfolio-account').value='7'; document.getElementById('portfolio-account').dispatchEvent(new Event('change'))`);
    assert.equal(await evaluate(`document.querySelectorAll('#opening-positions-list tr').length`), 1);
    await evaluate(`document.getElementById('portfolio-account').value=''; document.getElementById('portfolio-account').dispatchEvent(new Event('change'))`);
    await evaluate(`globalThis.beforeReload=true`);
    await cdp('Page.reload', { ignoreCache: true });
    await until(`globalThis.beforeReload===undefined && document.getElementById('position-count')?.textContent==='3'`);
    const oldProcessId = server.process.pid;
    await stop(server.process);
    server = await startBackend();
    assert.notEqual(server.process.pid, oldProcessId);
    await evaluate(`globalThis.beforeRestart=true`);
    await cdp('Page.navigate', { url: server.address });
    await until(`globalThis.beforeRestart===undefined && document.getElementById('position-count')?.textContent==='3' && document.getElementById('account-count')?.textContent==='2'`);
    execFileSync(python, ['-B', '-c', `
import sqlite3,sys
with sqlite3.connect(sys.argv[1]) as connection:
    assert connection.execute('SELECT quantity_micros FROM opening_positions ORDER BY id').fetchall()==[(2250000,), (1,), (9223372036854775807,)]
`, database]);
    console.log('PASS: HTTP error feedback, invalid input, account filter, browser reload and backend process restart.');
    await evaluate(`globalThis.originalFetch=fetch; globalThis.fetch=()=>Promise.reject(new TypeError('Synthetic offline')); document.getElementById('get-opening-positions').click()`);
    await until(`!document.getElementById('get-opening-positions').disabled`);
    assert.match(await evaluate(`document.getElementById('status-label').textContent`), /not been refreshed/);
    assert.equal(await evaluate(`document.querySelectorAll('#opening-positions-list tr').length`), 3);
    await evaluate(`globalThis.fetch=originalFetch; document.getElementById('get-opening-positions').click()`);
    await until(`document.getElementById('status-label').textContent===''`);
    await evaluate(`globalThis.fetch=async()=>new Response('Synthetic non-JSON response',{status:502}); document.getElementById('get-opening-positions').click()`);
    await until(`!document.getElementById('get-opening-positions').disabled`);
    assert.match(await evaluate(`document.getElementById('status-label').textContent`), /not been refreshed/);
    await evaluate(`globalThis.fetch=()=>{globalThis.pendingSaves=(globalThis.pendingSaves||0)+1;return new Promise((accept,reject)=>globalThis.rejectSave=reject)};
        document.getElementById('account-id').value='2';
        document.getElementById('ticker').value='PENDING';
        document.getElementById('quantity').value='1';
        document.getElementById('opening-form').requestSubmit();
        document.getElementById('opening-form').requestSubmit();`);
    assert.equal(await evaluate(`globalThis.pendingSaves`), 1);
    assert.ok(await evaluate(`document.getElementById('open-holding').disabled`));
    await evaluate(`globalThis.rejectSave(new TypeError('Synthetic failed save'))`);
    await until(`!document.getElementById('open-holding').disabled`);
    assert.match(await evaluate(`document.getElementById('open-holdings-list').textContent`), /Refresh positions before trying again/);
    await evaluate(`globalThis.fetch=originalFetch; document.getElementById('get-opening-positions').click(); document.getElementById('ticker').value=''; document.getElementById('quantity').value=''`);
    await until(`document.getElementById('status-label').textContent===''`);
    console.log('PASS: non-JSON read, pending double-submit protection and ambiguous-save feedback.');
    // Exercise the account feature against the real API and disposable database.
    await evaluate(`globalThis.accountPosts=[];
        globalThis.fetch=(url,options)=>{
            if(url==='/api/v1/accounts' && options?.method==='POST') accountPosts.push(JSON.parse(options.body));
            return originalFetch(url,options);
        };
        document.getElementById('account-name').value='   ';
        document.getElementById('account-form').requestSubmit();`);
    assert.match(await evaluate(`document.getElementById('account-create-status').textContent`), /more than spaces/);
    assert.equal(await evaluate(`accountPosts.length`), 0);
    await evaluate(`document.getElementById('portfolio-account').value='7';
        document.getElementById('account-name').value='  Synthetic Long-term  ';
        document.getElementById('account-form').requestSubmit();`);
    await until(`document.getElementById('account-create-status').dataset.state==='success' && !document.getElementById('create-account').disabled`);
    assert.deepEqual(await evaluate(`accountPosts`), [{ name: 'Synthetic Long-term' }]);
    assert.equal(await evaluate(`document.getElementById('account-count').textContent`), '3');
    assert.equal(await evaluate(`document.getElementById('portfolio-account').value`), '7');
    assert.equal(await evaluate(`document.getElementById('account-id').selectedOptions[0].textContent`), 'Synthetic Long-term');
    const createdAccountId = await evaluate(`document.getElementById('account-id').value`);
    assert.equal(await evaluate(`document.getElementById('account-name').value`), '');
    await evaluate(`document.getElementById('account-name').value='sYnThEtIc LoNg-TeRm'; document.getElementById('account-form').requestSubmit()`);
    await until(`!document.getElementById('create-account').disabled`);
    assert.match(await evaluate(`document.getElementById('account-create-status').textContent`), /Error 409.*duplicate/i);
    assert.equal(await evaluate(`document.getElementById('account-name').value`), 'sYnThEtIc LoNg-TeRm');
    await enter(createdAccountId, 'SYNTHNEW', '1.000001');
    await until(`document.getElementById('position-count').textContent==='4'`);
    await evaluate(`document.getElementById('portfolio-account').value=''; document.getElementById('portfolio-account').dispatchEvent(new Event('change'))`);
    assert.deepEqual(await evaluate(`Array.from(document.querySelectorAll('#opening-positions-list tr'),row=>Array.from(row.cells,cell=>cell.textContent)).at(-1)`), ['SYSYNTHNEW', 'Synthetic Long-term', '1.000001']);
    console.log('PASS: blank-name precheck, exact POST payload, case-insensitive duplicate feedback, refreshed selectors and holding in new account.');

    await evaluate(`globalThis.fetch=(url,options)=>{
        if(url==='/api/v1/accounts' && !options?.method) return Promise.reject(new TypeError('Synthetic read failure'));
        return originalFetch(url,options);
    };
    document.getElementById('account-name').value='Synthetic Reserve'; document.getElementById('account-form').requestSubmit();`);
    await until(`!document.getElementById('create-account').disabled`);
    assert.match(await evaluate(`document.getElementById('account-create-status').textContent`), /Account created. Refresh accounts/);
    assert.ok(await evaluate(`document.getElementById('account-id').disabled`));
    await evaluate(`globalThis.fetch=originalFetch; document.getElementById('load-accounts').click()`);
    await until(`document.getElementById('account-count').textContent==='4'`);
    await evaluate(`globalThis.fetch=()=>{globalThis.pendingAccountSaves=(globalThis.pendingAccountSaves||0)+1;return new Promise((accept,reject)=>globalThis.rejectAccountSave=reject)};
        document.getElementById('account-name').value='Synthetic Pending';
        document.getElementById('account-form').requestSubmit(); document.getElementById('account-form').requestSubmit();`);
    assert.equal(await evaluate(`pendingAccountSaves`), 1);
    assert.ok(await evaluate(`document.getElementById('account-name').readOnly && document.getElementById('create-account').disabled`));
    await evaluate(`rejectAccountSave(new TypeError('Synthetic lost response'))`);
    await until(`!document.getElementById('create-account').disabled`);
    assert.match(await evaluate(`document.getElementById('account-create-status').textContent`), /Refresh accounts before trying again/);
    assert.equal(await evaluate(`pendingAccountSaves`), 1, 'Failed POST must not be automatically retried');
    await evaluate(`globalThis.fetch=originalFetch; globalThis.beforeAccountReload=true`);
    await cdp('Page.reload', { ignoreCache: true });
    await until(`globalThis.beforeAccountReload===undefined && document.getElementById('account-count')?.textContent==='4' && document.getElementById('position-count')?.textContent==='4'`);
    const accountProcessId = server.process.pid;
    await stop(server.process);
    server = await startBackend();
    assert.notEqual(server.process.pid, accountProcessId);
    await evaluate(`globalThis.beforeAccountRestart=true`);
    await cdp('Page.navigate', { url: server.address });
    await until(`globalThis.beforeAccountRestart===undefined && document.getElementById('account-count')?.textContent==='4' && document.getElementById('position-count')?.textContent==='4'`);
    assert.equal(await evaluate(`Array.from(document.getElementById('account-id').options).find(option=>option.value===${JSON.stringify(createdAccountId)})?.textContent`), 'Synthetic Long-term');
    execFileSync(python, ['-B', '-c', `
import sqlite3,sys
with sqlite3.connect(sys.argv[1]) as connection:
    assert connection.execute('SELECT name FROM accounts ORDER BY id').fetchall()==[('Synthetic Brokerage',),('Synthetic Retirement',),('Synthetic Long-term',),('Synthetic Reserve',)]
    assert connection.execute('SELECT quantity_micros FROM opening_positions ORDER BY id').fetchall()==[(2250000,), (1,), (9223372036854775807,), (1000001,)]
`, database]);
    console.log('PASS: create/read-failure distinction, pending-submit guard, ambiguous-save feedback, new account/holding browser reload and real backend restart.');
    await screenshot('desktop.png');
    await cdp('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
    assert.ok(await evaluate(`document.documentElement.scrollWidth<=innerWidth`), 'Page overflows mobile viewport');
    await screenshot('mobile.png');
    console.log('PASS: failed-read recovery and desktop/mobile viewport checks.');
    // Empty workspace uses this same disposable fixture, never the owner's database.
    execFileSync(python, ['-B', '-c', `
import sqlite3,sys
with sqlite3.connect(sys.argv[1]) as connection:
    connection.execute('DELETE FROM opening_positions')
    connection.execute('DELETE FROM accounts')
`, database]);
    await evaluate(`globalThis.beforeEmptyReload=true`);
    await cdp('Page.reload', { ignoreCache: true });
    await until(`globalThis.beforeEmptyReload===undefined && document.getElementById('account-count')?.textContent==='0'`);
    assert.ok(await evaluate(`document.getElementById('open-holding').disabled && !document.getElementById('create-account').disabled`));
    await evaluate(`document.getElementById('account-name').value='Synthetic First'; document.getElementById('account-form').requestSubmit()`);
    await until(`document.getElementById('account-create-status').dataset.state==='success' && !document.getElementById('open-holding').disabled`);
    assert.equal(await evaluate(`document.getElementById('account-id').selectedOptions[0].textContent`), 'Synthetic First');
    console.log('PASS: first-account creation from an empty workspace enables the holding form.');
    console.log('All data was synthetic. No application backend source or portfolio database was modified.');
} finally {
    if (socket) socket.close();
    await Promise.all([...children].map(stop));
    await rm(fixture, { recursive: true, force: true });
}
