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
  systemStatus: {
    title: "System Status",
    loading: "Loading status...",
    error: "Failed to reach API.",
    statusLabel: "Status:",
    versionLabel: "Version:",
    refreshButton: "Refresh Status",
  },
} as const;

export type ContentDictionary = typeof content;
