import copy
import json


class idGenerator():
    def __init__(self, prefix, startId):
        self.prefix = prefix
        self.startId = startId
        self.currentId = startId
    
    def getNextId(self):
        nextId = self.currentId
        self.currentId += 1
        return nextId

    def getnextLongId(self):
        id = self.getNextId()
        return self.prefix + str(id).zfill(12)    

def transformInstructorData(input):
    transformedJson = addIdToInstructor(input)
    transformedJson = deleteArchivedAttributeInstructor(transformedJson)

def test():

    filePath = "/home/nicolas/Desktop/projects/teammates/src/test/resources/data/EmailGeneratorTest.json"
    outputPath = "/home/nicolas/Desktop/projects/teammates/src/it/resources/data/SqlEmailGeneratorTest.json"

    inputFile = open(filePath, "r")
    initalInput = json.load(inputFile)

    coursesMap = {} # STORE Course ID: courseName
    sectionsMap = {} # Store uniquesectionName -> courseName + sectionName: id
    teamsMap = {} # Store uniqueTeamName -> courseName + sectionName + teamName: id
    GidToAccountMap = {}
    sessionNameToId = {} # courseId -> sectionName -> longId
    questionMap = {}
    responseMap = {} 
    instructorMap = {} # STORE GID: LONGID
    studentMap = {}
    notificationsMap = {}

    ID_PREFIX = "00000000-0000-4000-8000-"
    ACCOUNT_COUNTER = idGenerator(ID_PREFIX, 1)
    SECTION_COUNTER = idGenerator(ID_PREFIX, 101)
    TEAM_COUNTER = idGenerator(ID_PREFIX, 201)
    COURSE_COUNTER = idGenerator(ID_PREFIX, 301) # course has unique ID so unused
    STUDENT_COUNTER = idGenerator(ID_PREFIX, 401)
    INSTRUCTOR_COUNTER = idGenerator(ID_PREFIX, 501)
    FEEDBACK_SESSIONS_COUNTER = idGenerator(ID_PREFIX, 701)
    FEEDBACK_QUESTION_COUNTER = idGenerator(ID_PREFIX, 801)
    FEEDBACK_RESPONSE_COUNTER = idGenerator(ID_PREFIX, 901)

    # keyType: {name: id}
    idMap = {}
    teamMap = {}
    GOOGLE_ID_FIELD_NAME = "googleId"
    ENTITIES_MISSING_GID_FIELD = 0
    ENTITIES_NO_ACCOUNT = 0

    def addId(counter, collectionName, input):
        for entityJson in input[collectionName].values():
            longId = counter.getnextLongId()
            entityJson["id"] = longId
        
        return input

    def addIdToAccount(input):
        input = addId(ACCOUNT_COUNTER, "accounts", input)
        for accountJson in input["accounts"].values():
            accountGid = accountJson[GOOGLE_ID_FIELD_NAME]
            GidToAccountMap[accountGid] = accountJson["id"]
        
        return input
    
    def removeReadNotificationsFromAccount(input):
        for accountJson in input["accounts"].values():
            if accountJson.get("readNotifications") == None:
                continue
            del accountJson["readNotifications"]

        return input

    def addEmptyNotificationsObj(input):
        if input.get("notifications"):
            return input
        input["notifications"] = {}
        return input

    def addEmptyReadNotificationsObj(input):
        if input.get("readNotifications"):
            return input
        
        input["readNotifications"] = {}
        return input
    
    def addEmptyAccountRequestsObj(input):
        if input.get("accountRequests"):
            return input
        
        input["accountRequests"] = {}
        return input
    
    def addEmptyFeedbackResponseCommentsObj(input):
        if input.get("accountRequests"):
                return input
            
        input["accountRequests"] = {}
        return input
    # def addIdToCourse(input):
    #     for courseJson in input["courses"].values():
    #         longId = COURSE_COUNTER.getnextLongId()
    #         courseJson["id"] = longId
    #         courseName = courseJson["name"]
    #         coursesMap[id] = {"name": courseName}
        
    #     return input
    
    # def addCourseNameToMap(input):
    #     for courseJson in input["courses"].values():
    #         courseName = courseJson["name"]
    #         courseObj = coursesMap.get(courseName)
    #         courseObj["name"] = courseName
        
    #     return input
    def concatTitleCaseString(*args):
        res = ""
        for s in args:
            res += s.title().replace(" ", "")
        
        return res

    def addCourseNamesToMap(input):
        for courseJson in input["courses"].values():
            courseId = courseJson["id"]
            courseName = courseJson["name"]
            coursesMap[courseId] = courseName

        return input

    def removeCourseCreatedAt(input):
        for courseJson in input["courses"].values():
            if courseJson.get("createdAt") == None:
                continue
            del courseJson["createdAt"]
        return input
    
    def addEmptySectionObj(input):
        if input.get("sections"):
            return input
        
        input["sections"] = {}
        return input
    
    def createSectionJson(input):
        sectionsJSON = {}
        
        # Assign section numbers when you see a section belonging to a course for the first time
        courseToSection = {}
        for studentJson in input["students"].values():
            courseId = studentJson["course"]
            sectionName = studentJson["section"]

            if courseToSection.get(courseId) == None:
                courseToSection[courseId] = {}

            if courseToSection[courseId].get(sectionName) == None:
                sectionId = SECTION_COUNTER.getnextLongId()
                courseToSection[courseId][sectionName] = sectionId
                courseName = coursesMap[courseId]
                uniqueSectionName = concatTitleCaseString(courseName, sectionName)
                sectionsMap[uniqueSectionName] = sectionId
                sectionDetails = {"id": sectionId,
                                  "course": {
                                      "id": courseId
                                  },
                                  "name": sectionName}
                sectionsJSON[uniqueSectionName] = sectionDetails
        return sectionsJSON

    def scanJsonAndAddSections(input):
        sections = createSectionJson(input)
        input["sections"] = sections
        return input
    
    def addEmptyTeamObj(input):
        if input.get("teams"):
            return input
        
        input["teams"] = {}
        return input
    
    def createTeamJson(input):
        sectionsJSON = {}
        
        # Assign team numbers when you see a team belonging to a course for the first time
        courseToSectionToTeam = {}
        for studentJson in input["students"].values():
            courseId = studentJson["course"]
            sectionName = studentJson["section"]
            teamName = studentJson["team"]

            if courseToSectionToTeam.get(courseId) == None:
                courseToSectionToTeam[courseId] = {}

            if courseToSectionToTeam[courseId].get(sectionName) == None:
                courseToSectionToTeam[courseId][sectionName] = {}
            
            if courseToSectionToTeam[courseId][sectionName].get(teamName) == None:
                teamId = TEAM_COUNTER.getnextLongId()
                
                courseToSectionToTeam[courseId][sectionName][teamName] = teamId
                courseName = coursesMap[courseId]
                uniqueSectionName = concatTitleCaseString(courseName, sectionName)
                uniqueTeamName = concatTitleCaseString(courseName, sectionName, teamName)
                teamsMap[uniqueTeamName] = teamId
                sectionDetails = {"id": teamId,
                                  "section": {
                                      "id": sectionsMap[uniqueSectionName]
                                  },
                                  "name": teamName}
                sectionsJSON[uniqueSectionName] = sectionDetails
        return sectionsJSON

    def scanJsonAndAddTeams(input):
        teams = createTeamJson(input)
        input["teams"] = teams
        return input
    
    def addIdToFeedbackSession(input):
        input = addId(FEEDBACK_SESSIONS_COUNTER, "feedbackSessions", input)
        for sessionJson in input["feedbackSessions"].values():
            sessionName = sessionJson["feedbackSessionName"]
            courseId = sessionJson["courseId"]
            if sessionNameToId.get(courseId) == None:
                sessionNameToId[courseId] = {}
            
            sessionNameToId[courseId][sessionName] = sessionJson["id"]
        return input
    
    def renameFeedbackCourseNameFieldFeedbackSessio(input):
        for sessionJson in input["feedbackSessions"].values():
            sessionName = sessionJson["feedbackSessionName"]
            sessionJson["name"] = sessionName
            del sessionJson["feedbackSessionName"]
    
        return input

    def populateCourseforFeedbackSession(input):
        for sessionJson in input["feedbackSessions"].values():
            # Get course UUID
            courseId =sessionJson["courseId"]
            sessionJson["course"] = {"id": courseId }
            del sessionJson["courseId"]
        
        return input

    # TODO Port to new variable
    def removeDeprecatedFeedbackSessionAttr(input):
        deprecatedAttr = ["sentOpeningSoonEmail", "sentOpenEmail", "sentClosingEmail", "sentClosedEmail"]
        for sessionJson in input["feedbackSessions"].values():
            # Get course UUID
            for attr in deprecatedAttr:
                if sessionJson.get(attr):
                    del sessionJson[attr]
        
        return input
    
    def addIdToFeedbackQuestion(input):
        for questionJson in input["feedbackQuestions"].values():
            longId = FEEDBACK_QUESTION_COUNTER.getnextLongId()
            questionJson["id"] = longId

        return input
    
    def populateSessionForQuestion(input):
        for questionJson in input["feedbackQuestions"].values():
            # Get course UUID
            sessionName = questionJson["feedbackSessionName"]
            courseId = questionJson["courseId"]
            sessionId = sessionNameToId[courseId][sessionName]
            questionJson["feedbackSession"] = {"id": sessionId }
            del questionJson["feedbackSessionName"]
            del questionJson["courseId"]
        
        return input

    def addDescriptionFieldForQuestion(input):
        for questionJson in input["feedbackQuestions"].values():
            questionJson["description"] = "Placeholder description"
        return input
    
    def addIdToFeedbackResponse(input): 
        return addId(FEEDBACK_RESPONSE_COUNTER, "feedbackResponses", input)
    
    def populateSessionForResponse(input):
        for responseJson in input["feedbackResponses"].values():
            # Get course UUID
            sessionName = responseJson["feedbackSessionName"]
            courseId = responseJson["courseId"]
            sessionId = sessionNameToId[courseId][sessionName]
            responseJson["feedbackSession"] = {"id": sessionId }
            
        
        return input
    
    # def PopulateFeedbackQuestionForResponse(input):

    def populateGiverSectionForResponse(input):
        print(sectionsMap)
        for responseJson in input["feedbackResponses"].values():
            sectionName = responseJson["giverSection"]

            # Self evaluation - find users section
            # TODO figure this out
            # if sectionName == "None":
            #     sectionName = 
                
            courseId = responseJson["courseId"]
            courseName = coursesMap[courseId]
            uniqueSectionName = concatTitleCaseString(courseName, sectionName)
            sectionId = sectionsMap[uniqueSectionName]
            responseJson["giverSection"] = {"id": sectionId }
        return input
    
    def populateReceiverSectionForResponse(input):
        for responseJson in input["feedbackResponses"].values():
            sectionName = responseJson["recipientSection"]
            ## TODO is this the correct way of handling none
            if sectionName == "None":
                continue
            courseId = responseJson["courseId"]
            courseName = coursesMap[courseId]
            uniqueSectionName = concatTitleCaseString(courseName, sectionName)
            sectionId = sectionsMap[uniqueSectionName]
            responseJson["giverSection"] = {"id": sectionId }
        return input

    def deleteUnneededFieldsResponse(input):
        fields = ["feedbackSessionName", "courseId"]
        for responseJson in input["feedbackResponses"].values():
            for field in fields:
                if responseJson.get(field) != None:
                    del responseJson[field]
        return input
    
    def addIdToInstructor(input):
        return addId(INSTRUCTOR_COUNTER, "instructors", input)
    
    def populateCourseforInstructor(input):
        for instructorJson in input["instructors"].values():
            # Get course UUID
            courseId = instructorJson["courseId"]
            instructorJson["course"] = {"id": courseId }
            del instructorJson["courseId"]
        
        return input
    
    def populateAccountforInstructor(input):
        nonlocal ENTITIES_MISSING_GID_FIELD
        for instructorJson in input["instructors"].values():
            # Check if instructor has GID
            if instructorJson.get("googleId") == None:
                ENTITIES_MISSING_GID_FIELD += 1
                continue
            # Get course UUID
            gid = instructorJson.get("googleId")
            accountId = GidToAccountMap[gid]
            instructorJson["account"] = {"id": accountId }
            del instructorJson["googleId"]
        
        return input
    
    def renameDisplayedNameToDisplayNameInstructor(input):
        for instructorJson in input["instructors"].values():
            displayName = instructorJson["displayedName"]
            instructorJson["displayName"] = displayName
            del instructorJson["displayedName"]
        return input
    
    def convertRoleToNewTypeInstructor(input):
        oldToNewRoleMap = {
            "Co-owner": "INSTRUCTOR_PERMISSION_ROLE_COOWNER",
            "Manager": "INSTRUCTOR_PERMISSION_ROLE_MANAGER",
            "Observer": "INSTRUCTOR_PERMISSION_ROLE_OBSERVER",
            "Tutor": "INSTRUCTOR_PERMISSION_ROLE_TUTOR",
            "Custom": "INSTRUCTOR_PERMISSION_ROLE_CUSTOM"
        }
        for instructorJson in input["instructors"].values():
            originalRoleName = instructorJson["role"]
            newRoleName = oldToNewRoleMap.get(originalRoleName)
            if newRoleName == None:
                # Throw error
                return False
            instructorJson["role"] = newRoleName
        return input
    
    def removeDeprecatedInstructorAttr(input):
        deprecatedAttr = ["isArchived"]

        for instructorJson in input["instructors"].values():
            for attr in deprecatedAttr:
                if instructorJson.get(attr) != None:
                    del instructorJson[attr]
        
        return input
    
    
    def addIdToStudent(input):
        for studentJSon in input["students"].values():
            longId = STUDENT_COUNTER.getnextLongId()
            studentJSon["id"] = longId

        return input

    def populateCourseforStudent(input):
        for studentJSon in input["students"].values():
            # Get course UUID
            courseId = studentJSon["course"]
            studentJSon["course"] = {"id": courseId }
        
        return input
    
    def populateAccountforStudent(input):
        nonlocal ENTITIES_MISSING_GID_FIELD
        nonlocal ENTITIES_NO_ACCOUNT
        for studentJSon in input["students"].values():
            # Check if student has GID
            if studentJSon.get("googleId") == None:
                ENTITIES_MISSING_GID_FIELD += 1
                continue

            # Get course UUID
            gid = studentJSon.get("googleId")

            # Found that some Student entities had GID but no account existed
            if GidToAccountMap.get(gid):
                accountId = GidToAccountMap[gid]
                studentJSon["account"] = {"id": accountId }
            else:
                ENTITIES_NO_ACCOUNT += 1
            del studentJSon["googleId"]
        
        return input
    
    def populateTeamforStudent(input):
        for studentJSon in input["students"].values():
            courseId = studentJSon["course"]["id"]
            courseName = coursesMap[courseId]
            sectionName = studentJSon["section"]
            teamName = studentJSon["team"]
            # concatTitleCaseString(courseId, teamName)
            uniqueTeamName = concatTitleCaseString(courseName, sectionName, teamName)
            teamId = teamsMap[uniqueTeamName]
            studentJSon["team"] = {"id": teamId }
        
        return input

    def deleteUnneededFieldsStudents(input):
        # section is mapped via teams
        fields = ["section"]
        for studentsJson in input["students"].values():
            for field in fields:
                if studentsJson.get(field) != None:
                    del studentsJson[field]
        return input
    
    # def getUniqueCourseName(courseId, teamName):



    transformedJson = copy.deepcopy(initalInput)

    # Misc transfromation - Notifications
    ## TODO Do we need any acc requests?
    transformedJson = addEmptyNotificationsObj(transformedJson)
    transformedJson = addEmptyReadNotificationsObj(transformedJson)
    transformedJson = addEmptyAccountRequestsObj(transformedJson)
    transformedJson = addEmptyFeedbackResponseCommentsObj(transformedJson)


    # Account modification
    transformedJson = addIdToAccount(transformedJson)
    transformedJson = removeReadNotificationsFromAccount(transformedJson)

    # Course Modification
    transformedJson = addCourseNamesToMap(transformedJson)
    # transformedJson = removeCourseCreatedAt(transformedJson)

    # Section Modification
    transformedJson = addEmptySectionObj(transformedJson)
    transformedJson = scanJsonAndAddSections(transformedJson)

    # Team Modification
    transformedJson = addEmptyTeamObj(transformedJson)
    transformedJson = scanJsonAndAddTeams(transformedJson)

    # Feedback session Modifications
    transformedJson = addIdToFeedbackSession(transformedJson)
    transformedJson = populateCourseforFeedbackSession(transformedJson)
    transformedJson = removeDeprecatedFeedbackSessionAttr(transformedJson)
    transformedJson = renameFeedbackCourseNameFieldFeedbackSessio(transformedJson)

    # Feedback question Modifications
    # TODO add description field
    transformedJson["feedbackQuestions"] = {}
    # transformedJson = addIdToFeedbackQuestion(transformedJson)
    # transformedJson = populateSessionForQuestion(transformedJson)
    # transformedJson = addDescriptionFieldForQuestion(transformedJson)

    

    # Instructor modification
    transformedJson = addIdToInstructor(transformedJson)
    transformedJson = populateCourseforInstructor(transformedJson)
    transformedJson = populateAccountforInstructor(transformedJson)
    transformedJson = renameDisplayedNameToDisplayNameInstructor(transformedJson)
    transformedJson = convertRoleToNewTypeInstructor(transformedJson)
    transformedJson = removeDeprecatedInstructorAttr(transformedJson)

    # Student modification
    def isStudent1(item):
        print(item)
        k = item[0]
        return k.startswith("student1")
    
    def filterStudents(inputjson):
        filteredStudents = filter(isStudent1, inputjson["students"].items())
        inputjson["students"] = dict(filteredStudents)
        return inputjson

    transformedJson = addIdToStudent(transformedJson)
    transformedJson = populateCourseforStudent(transformedJson)
    transformedJson = populateAccountforStudent(transformedJson)
    transformedJson = populateTeamforStudent(transformedJson)
    transformedJson = deleteUnneededFieldsStudents(transformedJson)
    transformedJson = filterStudents(transformedJson)

    
    # Feedback responses Modifications
    # TODO add description field
    transformedJson["feedbackResponses"] = {}
    # transformedJson = addIdToFeedbackResponse(transformedJson)
    # transformedJson = populateSessionForResponse(transformedJson)
    # # transformedJson = PopulateFeedbackQuestionForResponse(transformedJson)
    # transformedJson = populateGiverSectionForResponse(transformedJson)
    # transformedJson = populateReceiverSectionForResponse(transformedJson)
    # transformedJson = deleteUnneededFieldsResponse(transformedJson)


# "feedbackResponses",
#     Students
# Deadline extensions
    migratedEntities = ["accounts", "accountRequests", "courses", "instructors", "sections", "teams", 
                        "feedbackSessions", "feedbackQuestions", "notifications", 
                        "readNotifications", "feedbackResponseComments", "students"
                    ]
    
    jsonOutput = { entity: transformedJson[entity] for entity in migratedEntities }
    outputFile = open(outputPath, "w")
    json.dump(jsonOutput, outputFile, indent=4)
    outputFile.close()

    print("Migrated file")
    print(f"Failed to map {ENTITIES_MISSING_GID_FIELD} entities")
    print(f"Failed to map {ENTITIES_NO_ACCOUNT} entities")

test()