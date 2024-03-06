package teammates.client.scripts.sql;

import teammates.common.util.HibernateUtil;
import teammates.sqllogic.api.Logic;

import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.CriteriaDelete;
import jakarta.persistence.criteria.CriteriaQuery;
import jakarta.persistence.criteria.Root;
import teammates.client.connector.DatastoreClient;
import teammates.client.util.ClientProperties;
import teammates.storage.entity.UsageStatistics;
import teammates.storage.sqlentity.Notification;
import teammates.storage.sqlentity.ReadNotification;

public class VerifyDataMigrationConnection extends DatastoreClient {
    private final Logic logic = Logic.inst();

    private VerifyDataMigrationConnection() {
        String connectionUrl = ClientProperties.SCRIPT_API_URL;
        String username = ClientProperties.SCRIPT_API_NAME;
        String password = ClientProperties.SCRIPT_API_PASSWORD;

        HibernateUtil.buildSessionFactory(connectionUrl, username, password);
    }

    public static void main(String[] args) throws Exception {
        new VerifyDataMigrationConnection().doOperationRemotely();
    }

    protected void verifySqlConnection() {
        // Assert count of dummy request is 0
        Long testAccountRequestCount = countPostgresEntities(teammates.storage.sqlentity.AccountRequest.class);
        System.out.println(String.format("Num of account request in SQL: %d", testAccountRequestCount));

        // Write 1 dummy account request
        System.out.println("Writing 1 dummy account request to SQL");
        // teammates.storage.sqlentity.AccountRequest newEntity = new
        // teammates.storage.sqlentity.AccountRequest();
        teammates.storage.sqlentity.AccountRequest newEntity = new teammates.storage.sqlentity.AccountRequest(
                "dummy-teammates-account-request-email@gmail.com",
                "dummy-teammates-account-request",
                "dummy-teammates-institute");
        HibernateUtil.beginTransaction();
        HibernateUtil.persist(newEntity);
        HibernateUtil.commitTransaction();

        // Assert count of dummy request is 1
        testAccountRequestCount = countPostgresEntities(teammates.storage.sqlentity.AccountRequest.class);
        System.out.println(String.format("Num of account request in SQL after inserting: %d", testAccountRequestCount));

        // Delete dummy account request
        HibernateUtil.beginTransaction();
        CriteriaDelete<teammates.storage.sqlentity.AccountRequest> cdAccountReq = HibernateUtil.getCriteriaBuilder()
                .createCriteriaDelete(
                        teammates.storage.sqlentity.AccountRequest.class);
        cdAccountReq.from(teammates.storage.sqlentity.AccountRequest.class);
        HibernateUtil.executeDelete(cdAccountReq);
        HibernateUtil.commitTransaction();

        // logic.deleteAccountRequest("dummy-teammates-account-request-email@gmail.com",
        // "dummy-teammates-institute");

        // Assert count of dummy request is 0
        testAccountRequestCount = countPostgresEntities(teammates.storage.sqlentity.AccountRequest.class);
        System.out.println(String.format("Num of account request in SQL after removing: %d", testAccountRequestCount));

    }

    protected void verifyCountsInDatastore() {
        // System.out.println(String.format("Num of accounts in Datastore: %d",
        // ofy().load().type(Account.class).count()));
        // System.out.println(String.format("Num of account requests in Datastore: %d",
        // ofy().load().type(AccountRequest.class).count()));
        System.out.println(
                String.format("Num of notifications in Datastore: %d", ofy().load().type(Notification.class).count()));
        System.out.println(String.format("Num of usage statistics in Datastore: %d", ofy().load()
                .type(UsageStatistics.class).count()));
    }

    @Override
    protected void doOperation() {
        verifyCountsInDatastore();
        verifySqlConnection();
    }

    private Long countPostgresEntities(Class<? extends teammates.storage.sqlentity.BaseEntity> entity) {
        HibernateUtil.beginTransaction();
        CriteriaBuilder cb = HibernateUtil.getCriteriaBuilder();
        CriteriaQuery<Long> cr = cb.createQuery(Long.class);
        Root<? extends teammates.storage.sqlentity.BaseEntity> root = cr.from(entity);

        cr.select(cb.count(root));

        Long count = HibernateUtil.createQuery(cr).getSingleResult();
        HibernateUtil.commitTransaction();
        return count;
    }
}
