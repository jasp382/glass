Network Analysis
====================




* **Network analysis with ESRI Software:**

- Documentation of ESRI Services for network analysis:

  * Tools:

    - https://pro.arcgis.com/en/pro-app/tool-reference/ready-to-use/an-overview-of-the-network-analysis-toolset.htm

    - https://developers.arcgis.com/rest/network/api-reference/route-asynchronous-service.htm

    - https://developers.arcgis.com/rest/network/api-reference/service-area-synchronous-service.htm#GUID-162CDAE1-EB2A-40E9-87B2-06058914D220

      

  * Authentication and tokens:

    - https://developers.arcgis.com/rest/users-groups-and-items/generate-token.htm
    - https://developers.arcgis.com/documentation/core-concepts/security-and-authentication/what-is-oauth-2/
    - https://developers.arcgis.com/labs/rest/get-an-access-token/
    - https://developers.arcgis.com/documentation/core-concepts/security-and-authentication/accessing-arcgis-online-services/

  

- **Analysis with OTP:**

  - Download and use of pre-built JARs:

    - wget https://repo1.maven.org/maven2/org/opentripplanner/otp/1.4.0/otp-1.4.0-shaded.jar
    - java -Xmx4G -jar otp-1.4.0-shaded.jar --build /home/$USER/otp --inMemory

    

  - _OTP Tools documentation_:

    - https://docs.opentripplanner.org/en/latest/Intermediate-Tutorial/
    - Planner REST Endpoint:
      * http://dev.opentripplanner.org/apidoc/1.0.0/resource_PlannerResource.html
      * http://dev.opentripplanner.org/apidoc/1.0.0/json_Response.html
      * http://dev.opentripplanner.org/apidoc/1.0.0/json_TripPlan.html
      * http://dev.opentripplanner.org/apidoc/1.0.0/json_Itinerary.html
      * http://dev.opentripplanner.org/apidoc/1.0.0/json_Leg.html
      * http://dev.opentripplanner.org/apidoc/1.0.0/json_EncodedPolylineBean.html