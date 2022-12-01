import com.oracle.bmc.ConfigFileReader;
import com.oracle.bmc.Region;
import com.oracle.bmc.auth.BasicAuthenticationDetailsProvider;
import com.oracle.bmc.auth.ConfigFileAuthenticationDetailsProvider;
import com.oracle.bmc.auth.ResourcePrincipalAuthenticationDetailsProvider;
import com.oracle.bmc.loggingingestion.LoggingClient;
import com.oracle.bmc.loggingingestion.model.LogEntry;
import com.oracle.bmc.loggingingestion.model.LogEntryBatch;
import com.oracle.bmc.loggingingestion.model.PutLogsDetails;
import com.oracle.bmc.loggingingestion.requests.PutLogsRequest;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

/**
 * Job sample in Java using the Resource Principal
 */
public class job_java {
    // TODO: Set the env. variables before testing!
    private static final String CONFIG_LOCATION = System.getenv("CONFIG");
    private static final String CONFIG_PROFILE = System.getenv("TENANCY");
    private static final String LOG_ID = System.getenv("LOG_OBJECT_OCID");

    public static void main(String[] args) {
        System.out.println("Java Job Sample");

        try{
            System.out.println("Config");
            BasicAuthenticationDetailsProvider provider = null;

            // auto switch between resource principal and local code testing
            String OCI_RESOURCE_PRINCIPAL_VERSION = System.getenv("OCI_RESOURCE_PRINCIPAL_VERSION");
            if(OCI_RESOURCE_PRINCIPAL_VERSION == null) {
                ConfigFileReader.ConfigFile configWithProfile = ConfigFileReader.parse(CONFIG_LOCATION, CONFIG_PROFILE);
                provider = new ConfigFileAuthenticationDetailsProvider(configWithProfile);
            }
            else {
                // ResourcePrincipalAuthenticationDetailsProvider
                provider = ResourcePrincipalAuthenticationDetailsProvider.builder().build();
            }

            System.out.println("Log Client");
            LoggingClient loggingClient = LoggingClient.builder().build(provider);
            loggingClient.setRegion(Region.US_ASHBURN_1);

            LogEntry logEntry = LogEntry.builder()
                    .data("..starting Logging now....")
                    .data("... and another one...")
                    .id("log.entry.id")
                    .time(new Date(System.currentTimeMillis()))
                    .build();

            List<LogEntry> logEntries = new ArrayList<>();
            logEntries.add(logEntry);

            LogEntryBatch logEntryBatch = LogEntryBatch.builder()
                    .entries(logEntries)
                    .type("Custom Log")
                    .source("LocalSource")
                    .defaultlogentrytime(new Date(System.currentTimeMillis()))
                    .build();

            List<LogEntryBatch> logEntryBatchList = new ArrayList<>();
            logEntryBatchList.add(logEntryBatch);


            PutLogsDetails putLogsDetails = PutLogsDetails.builder()
                    .logEntryBatches(logEntryBatchList)
                    .specversion("1.0")
                    .build();

            PutLogsRequest request = PutLogsRequest.builder()
                    .logId(LOG_ID)
                    .putLogsDetails(putLogsDetails)
                    .build();

            loggingClient.putLogs(request);

        }catch (Exception e){
            System.err.println(e);
        }
    }
}
