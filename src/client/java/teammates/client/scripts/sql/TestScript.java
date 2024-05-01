package teammates.client.scripts.sql;

import teammates.client.connector.DatastoreClient;

public class TestScript extends DatastoreClient{

    public static void main(String[] args) {
        TestScript script = new TestScript();
        script.doOperationRemotely();
    }

    @Override
    protected void doOperation() {
        
        String[] args = {};
        try {
            // Seed datastore
            SeedDb.main(args);
            // migrate non-course
            MigrateNonCourseEntities.main(args);
            // patch notif and account req created-at
            // PatchCreatedAtAccountRequest.main(args);
            // PatchCreatedAtTimeNotification.main(args);
            // verify non-course
            VerifyNonCourseEntities.main(args);
            // migrate course
            // DataMigrationForCourseEntitySql.main(args);
            // verify course
            // VerifyCourseEntityAttributes.main(args);
            // VerifyDataMigrationConnection.main(args);
        } catch (Exception e){
            
        }
    }
    
}
