/**
 * Interface for Geoportal top navigation bar link
 */
export interface NavLink {
    /**
     * link title in Portuguese
     */
    titlePT: string;        
    /**
     * link title in English
     */
    titleEN: string;        
    /**
     * link for content in Portuguese
     */
    redirectPT: string;     
    /**
     * link for content in English
     */
    redirectEN: string;     
    /**
     * flag for internal app link or external
     */
    internal: boolean;     
}