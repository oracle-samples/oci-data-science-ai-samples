import java.io.IOException;

/**
 * Client ML Jobs delete test.
 */
public class TestDelete {

    public static void main(String[] args) throws IOException {
        //
        System.out.println("Start Java ML Jobs Deleting Test");

        // TODO: Set the env. variables before testing!
        String CONFIG_LOCATION = System.getenv("CONFIG");
        String CONFIG_PROFILE = System.getenv("TENANCY");
        String COMPARTMENT_OCID = System.getenv("COMPARTMENT");
        String PROJECT_OCID = System.getenv("PROJECT");
        String SUBNET_OCID = System.getenv("SUBNET");
        String LOG_GROUP_UUID = System.getenv("LOGGROUP");

        System.out.println("* INIT");
        MLJobs client = new MLJobs(CONFIG_LOCATION,CONFIG_PROFILE,COMPARTMENT_OCID,PROJECT_OCID,SUBNET_OCID,LOG_GROUP_UUID);

        client.deleteJobRun("JOB RUN OCID COMES HERE");
        client.deleteJob("JOB OCID COMES HERE");

        System.out.println("* EXIT");
    }
}
