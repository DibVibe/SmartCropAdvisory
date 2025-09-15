export const formatDate = (
  date: string | Date,
  options?: Intl.DateTimeFormatOptions
): string => {
  try {
    const dateObj = typeof date === "string" ? new Date(date) : date;

    // Use a consistent locale and format
    return dateObj.toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      ...options,
    });
  } catch (error) {
    console.error("Date formatting error:", error);
    return "Invalid Date";
  }
};

export const formatDateTime = (date: string | Date): string => {
  try {
    const dateObj = typeof date === "string" ? new Date(date) : date;

    return dateObj.toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch (error) {
    console.error("DateTime formatting error:", error);
    return "Invalid Date";
  }
};

// For ISO string consistency
export const formatDateISO = (date: string | Date): string => {
  try {
    const dateObj = typeof date === "string" ? new Date(date) : date;
    return dateObj.toISOString().split("T")[0]; // Returns YYYY-MM-DD
  } catch (error) {
    console.error("ISO date formatting error:", error);
    return "";
  }
};
