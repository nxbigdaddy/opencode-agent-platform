#!/usr/bin/env node
/**
 * OpenCode Remote Agent - 远程OpenCode执行包装器
 * 
 * 用法:
 *   node remote-opencode.js "你的命令"
 * 
 * 配置:
 *   在 opencode.jsonc 中添加:
 *   {
 *     "commands": {
 *       "remote": "node <workspace>/opencodes/remote-opencode.js"
 *     }
 *   }
 */

const { spawn } = require('child_process');
const path = require('path');

// SSH配置
const SSH_CONFIG = {
  host: 'opencode-remote',  // 使用SSH config中的别名
  user: 'root',
  keyFile: '<workspace>/opencodes/id_ed25519_1panel-160',
  remoteOpencode: '/usr/bin/opencode'
};

// 获取命令行参数
const args = process.argv.slice(2);
const command = args.join(' ');

if (!command) {
  console.error('用法: remote-opencode "你的命令"');
  process.exit(1);
}

// 构建SSH命令
const sshArgs = [
  SSH_CONFIG.host,
  `${SSH_CONFIG.remoteOpencode} ${command}`
];

console.log(`[Remote] 在 ${SSH_CONFIG.host} 上执行: opencode ${command}`);

// 执行SSH命令
const ssh = spawn('ssh', sshArgs, {
  stdio: 'inherit',
  shell: false
});

ssh.on('close', (code) => {
  process.exit(code);
});

ssh.on('error', (err) => {
  console.error('[Remote] SSH连接失败:', err.message);
  process.exit(1);
});
