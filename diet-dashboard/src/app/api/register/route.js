import bcrypt from "bcrypt";
import { pool } from "@/../lib/db.js";

export async function POST(req) {
  try {
    const { email, password, name } = await req.json();

    if (!email || !password) {
      return new Response(JSON.stringify({ error: "Email and password are required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    const conn = await pool.connect();

    // Check if user already exists
    const existing = await conn.request()
      .input("email", email)
      .query("SELECT * FROM Users WHERE email=@email");

    if (existing.recordset.length > 0) {
      return new Response(JSON.stringify({ error: "User already exists" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Hash the password
    const hash = await bcrypt.hash(password, 10);

    // Insert new user
    await conn.request()
      .input("email", email)
      .input("hash", hash)
      .input("name", name || email)
      .query(`
        INSERT INTO Users (email, passwordHash, name, provider)
        VALUES (@email, @hash, @name, 'credentials')
      `);

    return new Response(JSON.stringify({ message: "User registered successfully" }), {
      status: 201,
      headers: { "Content-Type": "application/json" },
    });

  } catch (error) {
    console.error("Registration error:", error);
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
