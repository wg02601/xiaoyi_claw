/**
 * SMTP 邮件发送脚本
 * 支持通过 SMTP 协议发送邮件
 */

const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');

// 配置文件路径
const CONFIG_PATH = path.join(__dirname, '..', 'config', 'smtp-config.json');

/**
 * 加载 SMTP 配置
 */
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
      return config;
    }
    return null;
  } catch (error) {
    console.error('❌ 加载配置失败:', error.message);
    return null;
  }
}

/**
 * 创建邮件传输器
 */
function createTransporter(config) {
  return nodemailer.createTransport({
    host: config.host,
    port: config.port,
    secure: config.secure || false, // true for 465, false for other ports
    auth: {
      user: config.user,
      pass: config.pass
    },
    tls: {
      rejectUnauthorized: config.rejectUnauthorized !== false
    }
  });
}

/**
 * 发送邮件
 * @param {Object} options - 邮件选项
 * @param {string} options.to - 收件人邮箱
 * @param {string} options.subject - 邮件主题
 * @param {string} options.text - 纯文本内容
 * @param {string} options.html - HTML内容（可选）
 * @param {Array} options.attachments - 附件列表（可选）
 */
async function sendMail(options) {
  const config = loadConfig();
  
  if (!config) {
    console.error('❌ 未找到 SMTP 配置，请先运行配置命令');
    console.log('💡 运行: node scripts/send-mail.js config <host> <port> <user> <pass> [from]');
    return { success: false, error: 'SMTP not configured' };
  }

  const transporter = createTransporter(config);

  const mailOptions = {
    from: options.from || config.from || config.user,
    to: options.to,
    subject: options.subject,
    text: options.text,
    html: options.html,
    attachments: options.attachments
  };

  try {
    const info = await transporter.sendMail(mailOptions);
    console.log('✅ 邮件发送成功!');
    console.log('📧 Message ID:', info.messageId);
    console.log('📤 发送至:', options.to);
    console.log('📋 主题:', options.subject);
    return { success: true, messageId: info.messageId };
  } catch (error) {
    console.error('❌ 邮件发送失败:', error.message);
    return { success: false, error: error.message };
  }
}

/**
 * 保存 SMTP 配置
 */
function saveConfig(host, port, user, pass, from) {
  const configDir = path.dirname(CONFIG_PATH);
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }

  const config = {
    host,
    port: parseInt(port),
    user,
    pass,
    from: from || user,
    secure: parseInt(port) === 465,
    rejectUnauthorized: true
  };

  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  console.log('✅ SMTP 配置已保存');
  console.log('📋 配置文件:', CONFIG_PATH);
  console.log('   Host:', host);
  console.log('   Port:', port);
  console.log('   User:', user);
  console.log('   From:', config.from);
  return config;
}

/**
 * 显示当前配置
 */
function showConfig() {
  const config = loadConfig();
  if (!config) {
    console.log('❌ 未配置 SMTP');
    return;
  }
  console.log('📋 当前 SMTP 配置:');
  console.log('   Host:', config.host);
  console.log('   Port:', config.port);
  console.log('   User:', config.user);
  console.log('   From:', config.from);
  console.log('   Secure:', config.secure);
}

/**
 * 测试 SMTP 连接
 */
async function testConnection() {
  const config = loadConfig();
  if (!config) {
    console.error('❌ 未找到 SMTP 配置');
    return false;
  }

  const transporter = createTransporter(config);
  
  try {
    await transporter.verify();
    console.log('✅ SMTP 连接测试成功!');
    console.log('   服务器:', config.host + ':' + config.port);
    return true;
  } catch (error) {
    console.error('❌ SMTP 连接测试失败:', error.message);
    return false;
  }
}

/**
 * 命令行入口
 */
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case 'config':
      // 配置 SMTP: node send-mail.js config <host> <port> <user> <pass> [from]
      if (args.length < 5) {
        console.log('用法: node send-mail.js config <host> <port> <user> <pass> [from]');
        console.log('示例: node send-mail.js config smtp.qq.com 465 your@qq.com your-auth-code your@qq.com');
        process.exit(1);
      }
      saveConfig(args[1], args[2], args[3], args[4], args[5]);
      break;

    case 'show':
      showConfig();
      break;

    case 'test':
      await testConnection();
      break;

    case 'send':
      // 发送邮件: node send-mail.js send <to> <subject> <text>
      if (args.length < 4) {
        console.log('用法: node send-mail.js send <to> <subject> <text|filePath>');
        console.log('示例: node send-mail.js send recipient@example.com "测试邮件" "这是邮件内容"');
        console.log('     node send-mail.js send recipient@example.com "测试邮件" @./content.txt');
        process.exit(1);
      }
      
      let content = args[3];
      // 支持从文件读取内容（以@开头）
      if (content.startsWith('@')) {
        const filePath = content.substring(1);
        try {
          content = fs.readFileSync(filePath, 'utf8');
          console.log('📄 已从文件读取内容:', filePath);
        } catch (e) {
          console.error('❌ 无法读取文件:', filePath);
          process.exit(1);
        }
      }

      await sendMail({
        to: args[1],
        subject: args[2],
        text: content
      });
      break;

    case 'send-html':
      // 发送HTML邮件: node send-mail.js send-html <to> <subject> <htmlFile>
      if (args.length < 4) {
        console.log('用法: node send-mail.js send-html <to> <subject> <htmlFile>');
        process.exit(1);
      }
      
      try {
        const html = fs.readFileSync(args[3], 'utf8');
        await sendMail({
          to: args[1],
          subject: args[2],
          html: html
        });
      } catch (e) {
        console.error('❌ 无法读取HTML文件:', args[3]);
      }
      break;

    default:
      console.log('📧 SMTP Mailer v1.0.0');
      console.log('');
      console.log('命令:');
      console.log('  config <host> <port> <user> <pass> [from]  配置SMTP');
      console.log('  show                                        显示当前配置');
      console.log('  test                                        测试SMTP连接');
      console.log('  send <to> <subject> <text>                  发送纯文本邮件');
      console.log('  send-html <to> <subject> <htmlFile>         发送HTML邮件');
      console.log('');
      console.log('常用SMTP服务器:');
      console.log('  QQ邮箱:     smtp.qq.com:465 (需开启SMTP服务并使用授权码)');
      console.log('  163邮箱:    smtp.163.com:465 (需开启SMTP服务并使用授权码)');
      console.log('  Gmail:      smtp.gmail.com:587 (需启用应用专用密码)');
      console.log('  Outlook:    smtp.office365.com:587');
      console.log('  阿里企业邮:  smtp.qiye.aliyun.com:465');
  }
}

// 导出模块
module.exports = { sendMail, loadConfig, saveConfig, testConnection };

// 命令行执行
if (require.main === module) {
  main().catch(console.error);
}
