"use client";

import { useSession, signOut } from "next-auth/react";

export default function UserMenu() {
  const { data: session, status } = useSession();

  if (status !== "authenticated") return null;

  return (
    <div className="flex items-center gap-4">
      <span className="font-semibold">
        {session.user.name || session.user.email}
      </span>

      <button
        onClick={() => signOut({ callbackUrl: "/login" })}
        className="px-3 py-1 bg-white text-blue-600 font-semibold rounded hover:bg-gray-100"
      >
        Logout
      </button>
    </div>
  );
}
