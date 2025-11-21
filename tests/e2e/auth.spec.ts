import { test, expect } from "@playwright/test";

const unique = Date.now();
const BASE_UI = "http://127.0.0.1:8000/static";

test.describe("Authentication Flow", () => {

  // -----------------------------------
  // SUCCESS: Register with unique creds
  // -----------------------------------
  test("Register successfully with valid inputs", async ({ page }) => {
    const uname = `user_${unique}`;
    const email = `user_${unique}@example.com`;

    await page.goto(`${BASE_UI}/register.html`);

    await page.fill("#first_name", "Test");
    await page.fill("#last_name", "User");
    await page.fill("#username", uname);
    await page.fill("#email", email);
    await page.fill("#password", "StrongPass123!");
    await page.fill("#confirm_password", "StrongPass123!");

    await page.click("button.primary-btn");

    const msg = page.locator("#register-message");
    await expect(msg).toContainText(/successful/i);

    const token = await page.evaluate(() =>
      localStorage.getItem("access_token")
    );
    expect(token).not.toBeNull();
  });

  // -----------------------------------
  // SUCCESS: Login with same credentials
  // -----------------------------------
  test("Login successfully with valid credentials", async ({ page }) => {
    const uname = `user_${unique}`;
    await page.goto(`${BASE_UI}/login.html`);

    await page.fill("#username_or_email", uname);
    await page.fill("#password", "StrongPass123!");
    await page.click("button.primary-btn");

    const msg = page.locator("#login-message");
    await expect(msg).toContainText(/successful/i);

    const token = await page.evaluate(() =>
      localStorage.getItem("access_token")
    );
    expect(token).not.toBeNull();
  });

  // -----------------------------------
  // NEGATIVE: Short Password
  // -----------------------------------
  test("Registration fails for short password", async ({ page }) => {
    const uname = `short_${unique}`;
    const email = `short_${unique}@example.com`;

    await page.goto(`${BASE_UI}/register.html`);

    await page.fill("#first_name", "Test");
    await page.fill("#last_name", "User");
    await page.fill("#username", uname);
    await page.fill("#email", email);

    // FIX: Set BOTH password + confirm_password to short
    await page.fill("#password", "short");
    await page.fill("#confirm_password", "short");

    await page.click("button.primary-btn");

    const msg = page.locator("#register-message");
    await expect(msg).toContainText(/password/i);
  });

  // -----------------------------------
  // NEGATIVE: Password mismatch
  // -----------------------------------
  test("Registration fails if passwords do not match", async ({ page }) => {
    await page.goto(`${BASE_UI}/register.html`);

    await page.fill("#first_name", "Test");
    await page.fill("#last_name", "User");
    await page.fill("#username", `nomatch_${unique}`);
    await page.fill("#email", `nomatch_${unique}@example.com`);
    await page.fill("#password", "StrongPass123!");
    await page.fill("#confirm_password", "WrongPassword");

    await page.click("button.primary-btn");

    const msg = page.locator("#register-message");
    await expect(msg).toContainText(/match/i);
  });

  // -----------------------------------
  // NEGATIVE: Wrong password login
  // -----------------------------------
  test("Login fails with wrong password", async ({ page }) => {
    await page.goto(`${BASE_UI}/login.html`);

    await page.fill("#username_or_email", `user_${unique}`);
    await page.fill("#password", "WrongPass!");

    await page.click("button.primary-btn");

    const msg = page.locator("#login-message");
    await expect(msg).toContainText(/invalid/i);
  });
});
