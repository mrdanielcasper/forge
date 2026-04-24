export const content = {
  global: {
    brandName: "Solo OS",
    tagline: "Build software, not debt.",
  },
  actions: {
    save: "Save Changes",
    cancel: "Cancel",
    delete: "Delete",
    confirm: "Confirm",
    retry: "Try Again",
  },
  states: {
    loading: "Loading...",
    saving: "Saving...",
    error: "Something went wrong. Please try again.",
    empty: "No data found.",
  },
  validation: {
    required: "This field is required.",
    invalidUrl: "Please enter a valid URL.",
    invalidEmail: "Please enter a valid email address.",
  },
  // Feature-specific copy can be nested below
  features: {
    webhooks: {
      title: "Connect Discord Alerts",
      description: "Send workflow alerts to the Discord channel your team already uses.",
      success: "Discord webhook saved. Alerts will use this channel.",
    },
  },
} as const;

export type ContentDictionary = typeof content;
