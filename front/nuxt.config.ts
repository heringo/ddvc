// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ["@nuxtjs/tailwindcss", "shadcn-nuxt", "@nuxtjs/supabase"], //
  shadcn: {
    /**
     * Prefix for all the imported component
     */
    prefix: "",
    /**
     * Directory that the component lives in.
     * @default "./components/ui"
     */
    componentDir: "./components/ui",
  },

  supabase: {
    redirectOptions: {
      login: "/auth/login",
      callback: "/auth/callback",
      include: [],
      exclude: ["*"],
      cookieRedirect: false,
    },
    cookieOptions: {
      maxAge: 60 * 60 * 24 * 31,
      sameSite: "lax",
      secure: true,
    },
  },
});
