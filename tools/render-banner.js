const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({headless: 'new'});
  const page = await browser.newPage();
  await page.setViewport({width: 1280, height: 640});
  const htmlPath = path.resolve(__dirname, '..', 'docs', 'social-preview-banner.html');
  const fileUrl = 'file:///' + htmlPath.split(path.sep).join('/');
  await page.goto(fileUrl, {waitUntil: 'networkidle0', timeout: 15000});
  const banner = await page.$('.banner');
  await banner.screenshot({path: path.resolve(__dirname, '..', 'docs', 'social-preview.png')});
  await browser.close();
  console.log('OK: docs/social-preview.png rendered (1280x640)');
})().catch(e => console.error('FAIL:', e.message));
