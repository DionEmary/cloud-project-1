import NextAuth from "next-auth";
import GitHubProvider from "next-auth/providers/github";
import CredentialsProvider from "next-auth/providers/credentials";
import bcrypt from "bcrypt";
import { pool } from "@/../lib/db.js";

export const authOptions = {
  session: { strategy: "jwt" },

  providers: [
    // GitHub OAuth
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
    }),

    // Email + Password login
    CredentialsProvider({
      name: "Email & Password",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        try {
          const conn = await pool.connect();
          const result = await conn
            .request()
            .input("email", credentials.email)
            .query("SELECT * FROM Users WHERE email=@email");

          const user = result.recordset[0];
          if (!user) throw new Error("User not found");

          const valid = await bcrypt.compare(
            credentials.password,
            user.passwordHash
          );
          if (!valid) throw new Error("Invalid password");

          return { id: user.id, email: user.email, name: user.name };
        } catch (error) {
          console.error("Authorization error:", error);
          return null; // NextAuth requires null if auth fails
        }
      },
    }),
  ],

  callbacks: {
    async signIn({ user, account }) {
      try {
        // Only insert users for OAuth logins
        if (account.provider !== "credentials") {
          const conn = await pool.connect();
          await conn.request()
            .input("email", user.email)
            .input("name", user.name || user.email)
            .input("provider", account.provider)
            .query(`
              IF NOT EXISTS (SELECT 1 FROM Users WHERE email=@email)
              INSERT INTO Users (email, name, provider)
              VALUES (@email, @name, @provider)
            `);
        }
        return true;
      } catch (error) {
        console.error("SignIn callback error:", error);
        return false;
      }
    },

    async jwt({ token, user }) {
      // Attach user ID to JWT on login
      if (user?.id) token.id = user.id;
      return token;
    },

    async session({ session, token }) {
      // Include user ID in session
      session.user.id = token.id;
      return session;
    },
  },

  pages: {
    signIn: "/login", 
  },

  async redirect({ url, baseUrl }) {
    // Always redirect to homepage after login
    return baseUrl;
  },

  debug: process.env.NODE_ENV === "development",
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
