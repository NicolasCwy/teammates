package teammates.sqllogic.api;


import static org.mockito.Mockito.mock;

import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import teammates.common.datatransfer.SqlDataBundle;
import teammates.common.util.Config;
import teammates.common.util.EmailType;
import teammates.common.util.EmailWrapper;
import teammates.sqllogic.core.CoursesLogic;
import teammates.sqllogic.core.DeadlineExtensionsLogic;
import teammates.sqllogic.core.FeedbackSessionsLogic;
import teammates.sqllogic.core.UsersLogic;
import teammates.storage.sqlentity.Student;
import teammates.test.BaseTestCase;
import teammates.test.EmailChecker;

/**
 * SUT: {@link SqlEmailGenerator}.
 */
public class EmailGeneratorTest extends BaseTestCase {

    private CoursesLogic coursesLogic;

    private DeadlineExtensionsLogic deLogic;

    private FeedbackSessionsLogic fsLogic;

    private UsersLogic usersLogic;

    private final SqlEmailGenerator emailGenerator = SqlEmailGenerator.inst();

    private SqlDataBundle dataBundle;

    @BeforeMethod
    public void setUpMethod() {
        dataBundle = loadSqlDataBundle("/SqlEmailGeneratorTest.json");

        coursesLogic = mock(CoursesLogic.class);
        deLogic = mock(DeadlineExtensionsLogic.class);
        fsLogic = mock(FeedbackSessionsLogic.class);
        usersLogic = mock(UsersLogic.class);
        
        emailGenerator.initLogicDependencies(coursesLogic, deLogic, fsLogic, usersLogic);
    }

    @Test
    public void testGenerateSessionLinksRecoveryEmail() throws Exception {

        ______TS("invalid email address");

        EmailWrapper email = emailGenerator.generateSessionLinksRecoveryEmailForStudent(
                "non-existing-student");
        String subject = EmailType.SESSION_LINKS_RECOVERY.getSubject();

        verifyEmail(email, "non-existing-student", subject,
                "/sessionLinksRecoveryNonExistingStudentEmail.html");

        ______TS("no sessions found");

        Student student1InCourse1 = dataBundle.students.get("student1InCourse1");

        email = emailGenerator.generateSessionLinksRecoveryEmailForStudent(
                student1InCourse1.getEmail());
        subject = EmailType.SESSION_LINKS_RECOVERY.getSubject();

        verifyEmail(email, student1InCourse1.getEmail(), subject,
                "/sessionLinksRecoveryNoSessionsFoundEmail.html");

        // ______TS("Typical case: found opened or closed but unpublished Sessions");

        // Student student1InCourse3 = dataBundle.students.get("student1InCourse3");

        // email = emailGenerator.generateSessionLinksRecoveryEmailForStudent(
        //         student1InCourse3.getEmail());

        // subject = EmailType.SESSION_LINKS_RECOVERY.getSubject();

        // verifyEmail(email, student1InCourse3.getEmail(), subject,
        //         "/sessionLinksRecoveryOpenedOrClosedButUnpublishedSessions.html");

        // ______TS("Typical case: found opened or closed and  published Sessions");

        // Student student1InCourse4 = dataBundle.students.get("student1InCourse4");

        // email = emailGenerator.generateSessionLinksRecoveryEmailForStudent(
        //         student1InCourse4.getEmail());

        // subject = EmailType.SESSION_LINKS_RECOVERY.getSubject();

        // verifyEmail(email, student1InCourse4.getEmail(), subject,
        //         "/sessionLinksRecoveryOpenedOrClosedAndpublishedSessions.html");
    }

    private void verifyEmail(EmailWrapper email, String recipient, String subject, String emailContentFilePath)
            throws Exception {
        // check recipient
        assertEquals(recipient, email.getRecipient());

        // check subject
        assertEquals(subject, email.getSubject());

        // check sender name
        assertEquals(Config.EMAIL_SENDERNAME, email.getSenderName());

        // check sender email
        assertEquals(Config.EMAIL_SENDEREMAIL, email.getSenderEmail());

        // check reply to address
        assertEquals(Config.EMAIL_REPLYTO, email.getReplyTo());

        String emailContent = email.getContent();

        // check email body for expected content
        EmailChecker.verifyEmailContent(emailContent, emailContentFilePath);

        // check email body for no left placeholders
        assertFalse(emailContent.contains("${"));
    }
}
