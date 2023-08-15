/**
 * Interface for app language selection
 */
export interface Language {
    /**
     * reference to country code to get country flag
     */
    country: string;
    /**
     * language name to be displayed
     */
    language: string;
}