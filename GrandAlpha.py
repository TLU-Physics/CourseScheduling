from math import sqrt,exp
from random import random,choice
from os.path import exists

from DataStructures import *

class GrandAlpha:
    def __init__(self, schinitFilename, conflictsFilename, timeConflictsFilename):
        # load the valid time labels (for error checking) and detail (for report)
        validTimesFilename = 'ValidTimes.txt'
        validTimesFile = open(validTimesFilename, 'r')
        self.validTimes = {}
        for line in validTimesFile:
            if len(line.strip()) > 0 and line.strip()[0] != '#':
                elements = line.strip().split(',')
                timecode = elements[0]
                self.validTimes[timecode] = TimeDetail(elements[1], elements[2], elements[3])
        
        validTimesFile.close()
        
        crossListingsFilename = 'CrossListings.txt'
        coursesToIgnore, crosslistingmap = GrandAlpha.loadCrossListings(crossListingsFilename)
        
        # load the information about what courses are being taught
        schinitFile = open(schinitFilename, 'r')
        course_list = []
        self.course_list_multisection = []
        schinitFile.readline() # skip header
        for line in schinitFile:
            if len(line.strip()) > 0:
                elements = line.strip().split(',')
                if len(elements) < 14:
                    raise Exception('There does not appear to be enough data in the file to be used as a detailed input file. 14 columns needed. Not enough data found on the following line:\n' + line)
                
                registrar_crs_cde = elements[1].strip()
                crs_cde_elements = registrar_crs_cde.split(' ')
                courseid = crs_cde_elements[0] + crs_cde_elements[1]
                if courseid not in coursesToIgnore:
                    if courseid in course_list:
                        if courseid not in self.course_list_multisection:
                            self.course_list_multisection.append(courseid)
                    else:
                        course_list.append(courseid)
        
        schinitFile.close()
        
        # load the information about what possible times each course can be taught at
        # and load the information about what courses faculty are teaching
        schinitFile = open(schinitFilename, 'r')
        self.allCourseTimes = AllCourseTimes()
        self.allFacCourses = AllFacultyCourses() # this will be the list of faculty schedulesfor line in schinitFile:
        previous_courseid = ''
        section_count = 1
        schinitFile.readline() # skip header
        for line in schinitFile:
            if len(line.strip()) > 0:
                # TODO: commas in course names are problematic
                elements = line.strip().split(',')
                
                registrar_crs_cde = elements[1].strip()
                crs_cde_elements = registrar_crs_cde.split(' ')
                courseid = crs_cde_elements[0] + crs_cde_elements[1]
                if courseid not in coursesToIgnore:
                    course_name = courseid
                    if courseid in self.course_list_multisection:
                        if courseid != previous_courseid: # the courses must be in order for this to work
                            section_count = 1
                        course_name += '-' + str(section_count)
                        section_count += 1
                    # TODO: try to preserve section note?
                    courseTimes = CourseTimes(category = elements[0], name = course_name, hours = elements[2], cde = elements[3], timecode = elements[5], building = elements[9], room = elements[10], cap = elements[12])
                    for t in courseTimes.times:
                        if t not in self.validTimes:
                            raise ValueError(t + ' (for ' + courseTimes.name + ') is not in the list of valid times')
                    self.allCourseTimes.append(courseTimes)
                    facultyName = elements[11].strip()
                    facCourses = self.allFacCourses.getFacultyCoursesItemByName(facultyName)
                    if facCourses == None:
                        facultyLine = facultyName + ',' + course_name
                        facCourses = FacultyCourses(facultyLine, dept = elements[0])
                        self.allFacCourses.append(facCourses)
                    else:
                        facCourses.courses.append(course_name.strip())
                    previous_courseid = courseid

        schinitFile.close()
        
        allCoursesList = self.allCourseTimes.getAllCourses()
        
        # load the information about the course conflicts that exist that the new
        # schedule must adapt to
        conflictsFile = open(conflictsFilename, 'r')
        self.allConflicts = AllConflicts()
        for line in conflictsFile:
            if len(line.strip()) > 0 and line.strip()[0] != '#':
                semipos = line.find(';')
                priority = ""
                if semipos > 0:
                    priority = line[semipos + 1:]
                    line = line[:semipos]
                courses = line.strip().split(',')
                
                # check to make sure the courses in the list exist
                for course in courses:
                    if course not in allCoursesList:
                        if course + '-1' not in allCoursesList:
                            print('The course', course, 'is not in the master list of courses')
                            raise Exception
                
                if priority == "":
                    self.allConflicts.addCluster(courses)
                else:
                    self.allConflicts.addCluster(courses, priority)

        conflictsFile.close()

        # load the information about the time conflicts that exist
        # this defines times that should be considered overlapping
        timeConflictsFile = open(timeConflictsFilename, 'r')
        self.allTimeConflicts = []
        for line in timeConflictsFile:
            if len(line.strip()) > 0 and line.strip()[0] != '#':
                els = line.strip().split(',')
                if els[0] not in self.validTimes:
                    raise ValueError(els[0] + ' is not in the list of valid times (' + line.strip() + ')')
                if els[1] not in self.validTimes:
                    raise ValueError(els[1] + ' is not in the list of valid times (' + line.strip() + ')')
                self.allTimeConflicts.append(TimeConflict(els[0], els[1]))

        timeConflictsFile.close()

    def doTimesConflict(self, time1, time2):
        if time1 == time2:
            return True
        if time1 > time2:
            time1, time2 = time2, time1
        for conflict in self.allTimeConflicts:
            if time1 == conflict.time1 and time2 == conflict.time2:
                return True
        return False
    
    def CreateRandomScheduleBasic(self):
        # just choose a random time for every course
        return {courseTimes.name: choice(courseTimes.times) for courseTimes in self.allCourseTimes.allCourseTimes}
    
    def CreateRandomScheduleTry(self):
        """Attempts to create a new schedule at random
        
        This function makes sure to take into account faculty schedules so that the
        schedule produced is guaranteed to satisfy faculty constraints.
        The attempt may not be successful.
        
        Returns:
            dictionary: the schedule created if successful and an empty dict if
                unsuccessful
        """
        
        # TODO: take into account multiple sections of same class
        # should be okay for now because I am only listing one possiblity for courses with
        # multiple sections
        sch = {}
        for courseTimes in self.allCourseTimes.allCourseTimes:
            # build a list of other times that should be excluded based on the
            # professor's schedule
            otherCoursesToCheck = self.allFacCourses.getFacOtherCoursesByCourse(courseTimes.name)
            otherTimes = []
            for course in otherCoursesToCheck:
                if course in sch:
                    otherTimes.append(sch[course])

            # build a list of times that do not conflict based on the professor's schedule
            possibletimes = []
            for time in courseTimes.times:
                timeOkay = True
                for otherTime in otherTimes:
                    if self.doTimesConflict(time, otherTime):
                        timeOkay = False
                        break
                if timeOkay:
                    possibletimes.append(time)
            
            if len(possibletimes) == 0:
                print('Reached an impasse when building initial schedule with trying to schedule courses for ', self.allFacCourses.getFacNameByCourse(courseTimes.name), '. Trying again...', sep = '')
                return {}

            # select one possible time at random
            sch[courseTimes.name] = choice(possibletimes)
            
        return sch
    
    def CreateRandomSchedule(self):
        """Creates a new schedule at random
        
        This function makes sure to take into account faculty schedules so that the
        schedule produced is guaranteed to satisfy faculty constraints
        
        Returns:
            dictionary: the schedule created where each key is a course name
                and each value is a time
        
        Raises:
            Exception: It may take multiple trials to produce a schedule
                because of too little freedom in multiple courses a professor is
                teaching. If too many attempts are made, then raise an exception
                and the user should look at loosening the restrictions
        """
        
        tryCount = 0
        while True:
            tryCount += 1
            if tryCount > 30:
                print('Having trouble creating any schedule based on faculty restrictions given')
                raise Exception
            
            sch = self.CreateRandomScheduleTry()
            if len(sch) != 0:
                return sch
    
    def StepSchedule(self, sch):
        sch = sch.copy()
        
        tryCount = 0
        while True:
            tryCount += 1
            if tryCount > 30:
                print('Having trouble stepping schedule for unknown reason')
                raise Exception
            
            # TODO: take into account multiple sections of same class
            # should be okay for now because I am only listing one possiblity for courses with
            # multiple sections

            courseToChange = choice(list(sch.keys()))
            courseTimes = self.allCourseTimes.getCourseTimes(courseToChange)
            currentTime = sch[courseToChange]
            
            if len(courseTimes.times) == 1: # If the course only has one time slot available, it cannot be changed
                tryCount -= 1 # don't count this against the total number of trials
                continue

            otherCoursesToCheck = self.allFacCourses.getFacOtherCoursesByCourse(courseToChange)
            otherTimes = []
            for course in otherCoursesToCheck:
                otherTimes.append(sch[course])

            # build a list of times that do not conflict based on the professor's schedule
            possibletimes = []
            for time in courseTimes.times:
                if time == currentTime:
                    continue
                timeOkay = True
                for otherTime in otherTimes:
                    if self.doTimesConflict(time, otherTime):
                        timeOkay = False
                        break
                if timeOkay:
                    possibletimes.append(time)
                    
            if len(possibletimes) != 0:
                sch[courseToChange] = choice(possibletimes)
                #print(tryCount)
                return sch

    def accumulatePenalties(self, sch, verbose = False):
        # get a dict where the times are the keys and the courses are the values
        inv_sch = {}
        for k, v in sch.items():
            inv_sch.setdefault(v, []).append(k)
        
        totalPenalties = 0
        # for each time, find all courses at that time and test every combination
        # for conflicts
        for time, courses in inv_sch.items():
            for i in range(len(courses)):
                for j in range(i + 1, len(courses)):
                    penalties = self.allConflicts.getPenalty(courses[i], courses[j])
                    totalPenalties += penalties
                    if penalties > 0 and verbose:
                        print(courses[i], 'and', courses[j], 'conflict with penalty', penalties)
        
        # for each 2 times that overlap, find all courses in each of the 2 groups
        # and test every possible pair
        for timeConflict in self.allTimeConflicts:
            if timeConflict.time1 in inv_sch and timeConflict.time2 in inv_sch:
                for course1 in inv_sch[timeConflict.time1]:
                    for course2 in inv_sch[timeConflict.time2]:
                        penalties = self.allConflicts.getPenalty(course1, course2)
                        totalPenalties += penalties
                        if penalties > 0 and verbose:
                            print(course1, 'and', course2, 'conflict with penalty', penalties)
        
        # multiple sections are handled within the AllConflicts class
        # the getPenalty function has special behavior for multi-section courses
        
        return totalPenalties
    
    def anneal(self, initialsch, Tinitial):
        # TODO: once the penalties hit 0, this should just stop running
        Tmin = 0.1
        tau = 1e4

        t = 0
        T = Tinitial
        sch = initialsch.copy()
        penalties = self.accumulatePenalties(sch)
        while T > Tmin:
            
            # show progress
            if t % 5000 == 0:
                print('Steps taken:', t, '   penalties:', penalties)

            # Cooling
            T = Tinitial * exp(-t/tau)

            schnew = self.StepSchedule(sch)
            penaltiesnew = self.accumulatePenalties(schnew)
            deltaPenalties = penaltiesnew - penalties

            # accept the new sch according to Boltzmann factor
            if random() < exp(-deltaPenalties / T):
                sch = schnew
                penalties = penaltiesnew
            
            t += 1
        
        return sch
    
    def findOptimalSchedule(self, trials):
        Tinitial = 100
        
        optpenalties = 99999
        for i in range(trials):
            
            initialsch = self.CreateRandomSchedule()
            schnew = self.anneal(initialsch, Tinitial)
            penaltiesnew = self.accumulatePenalties(schnew, verbose = True)
            print('Trial', i + 1, 'gave a schedule with', penaltiesnew, 'penalties')
            if penaltiesnew < optpenalties:
                optsch = schnew
                optpenalties = penaltiesnew
            if optpenalties == 0:
                print("This schedule has 0 penalties. Finishing.")
                break
        
        return optsch

    def summary(self, sch):
        penalties = self.accumulatePenalties(sch, verbose = True)
        print('The total number of penalties for the schedule is', penalties)
        
        # TODO: need more detail - like where are the penalties coming from?
    
    def exportSch(self, filename, sch):
        outfile = open(filename, 'w')
        facCoursesList = self.allFacCourses.allFacCourses.copy()
        facCoursesList.sort(key = lambda facCourses: facCourses.dept + facCourses.name)
        currentDept = facCoursesList[0].dept
        for facCourses in facCoursesList:
            if facCourses.dept != currentDept:
                outfile.write('\n')
                currentDept = facCourses.dept
            for course in facCourses.courses:
                s = facCourses.name + ',' + course + ',' + sch[course] + '\n'
                outfile.write(s)
        
        outfile.close()
    
    def exportSchDetail(self, filename, sch, addCrossListings = True):
        
        # load the course names
        courseNamesFilename = 'CourseNames.txt'
        courseNames = {}
        if exists(courseNamesFilename):
            courseNamesFile = open(courseNamesFilename, 'r')
            for line in courseNamesFile:
                linest = line.strip()
                if len(linest) > 0 and linest[0] != '#':
                    # careful about commas inside the course name
                    commapos = linest.find(',')
                    courseid = linest[:commapos]
                    courseNames[courseid] = linest[commapos + 1:]
            courseNamesFile.close()
        else:
            print('Could not find file', courseNamesFilename, 'so course names will not be included')
        
        competencyFilename = 'CompetencyList.txt'
        competencymap = {}
        if exists(competencyFilename):
            competencyFile = open(competencyFilename, 'r')
            for line in competencyFile:
                if len(line.strip()) > 0 and line.strip()[0] != '#':
                    elements = line.strip().split(',')
                    cid = elements[0]
                    competencymap[cid] = elements[1]
            competencyFile.close()
        else:
            print('Could not find file', competencyFilename, 'so competency info will not be included')
        
        crossListingsFilename = 'CrossListings.txt'
        coursesToAdd = []
        crosslistingmap = {}
        if addCrossListings:
            coursesToAdd, crosslistingmap = GrandAlpha.loadCrossListings(crossListingsFilename)
        
        outfile = open(filename, 'w')
        s = 'category,crs_cde,hrs,cde,crs_title,timecode,days,begin_time,end_time,bldg,room,instructor_name,cap,section_note\n'
        outfile.write(s)
        
        allCoursesList = self.allCourseTimes.getAllCourses().copy()
        
        # insert cross listings into list of courses to include in report
        for course in allCoursesList:
            courseid = CourseTimes.getCourseDeptCode(course) + CourseTimes.getCourseNum(course)
            if courseid in crosslistingmap and courseid not in coursesToAdd:
                otherCourse = GrandAlpha.getCrossListedCourse(course, crosslistingmap)
                allCoursesList.append(otherCourse)
        
        allCoursesList.sort(key = lambda course: self.allCourseTimes.getCourseDept(course) + course)
        
        for course in allCoursesList:
            
            courseid = CourseTimes.getCourseDeptCode(course) + CourseTimes.getCourseNum(course)
            
            course_code = CourseTimes.getCourseDeptCode(course) + ' ' + CourseTimes.getCourseNum(course) + '  ' + CourseTimes.getCourseSectionNum(course)
            if courseid in competencymap:
                competency = competencymap[courseid]
                course_code = course_code + '   ' + competency
            
            course_name = ""
            if courseid in courseNames:
                course_name = courseNames[courseid]
            
            section_note = ""
            if courseid in crosslistingmap:
                otherCourseid = crosslistingmap[courseid]
                courseName = CourseTimes.getCourseDeptCode(otherCourseid) + ' ' + CourseTimes.getCourseNum(otherCourseid)
                section_note = 'Cross Listed as ' + courseName
            
            # get schedule info, but this depends on whether the course is cross listed
            if courseid not in coursesToAdd: # it is the primary of the cross listing or is not cross listed
                timecode = sch[course]
                instructor = self.allFacCourses.getFacNameByCourse(course)
                category, hours, cde, building, room, capacity = self.allCourseTimes.getCourseInfo(course)
            else: # it is the secondary of the cross listing
                otherCourse = GrandAlpha.getCrossListedCourse(course, crosslistingmap)
                timecode = sch[otherCourse]
                instructor = self.allFacCourses.getFacNameByCourse(otherCourse)
                category, hours, cde, building, room, capacity = self.allCourseTimes.getCourseInfo(otherCourse)
                category = self.allCourseTimes.getCourseDept(course)
                hours = "0"
            
            timeinfo = self.validTimes[timecode]
            
            s = category + ',' + course_code + ',' + hours + ',' + cde + ',' + course_name + ',' + timecode + ',' + timeinfo.day + ',' + timeinfo.start + ',' + timeinfo.end + ',' + building + ',' + room + ',' + instructor + ',' + capacity + ',' + section_note + '\n'
            outfile.write(s)
            
        outfile.close()
        
    def loadCrossListings(crossListingsFilename):
        crosslistinglist = []
        crosslistingmap = {}
        if exists(crossListingsFilename):
            crossListingsFile = open(crossListingsFilename, 'r')
            for line in crossListingsFile:
                if len(line.strip()) > 0 and line.strip()[0] != '#':
                    elements = line.strip().split(',')
                    crosslistinglist.append(elements[1])
                    crosslistingmap[elements[0]] = elements[1]
                    crosslistingmap[elements[1]] = elements[0]
            crossListingsFile.close()
        else:
            print('Could not find file', crossListingsFilename, 'so cross listings will not be included')
        
        return crosslistinglist, crosslistingmap
        
    def getCrossListedCourse(course, crosslistingmap):
        courseid = CourseTimes.getCourseDeptCode(course) + CourseTimes.getCourseNum(course)
        
        hyphenpos = course.find('-')
        sectionNumberPart = ""
        if hyphenpos > 0:
            sectionNumberPart = course[hyphenpos:]
        
        othercourseid = crosslistingmap[courseid]
        return othercourseid + sectionNumberPart
    
    def importSch(self, filename, detail = True):
        crossListingsFilename = 'CrossListings.txt'
        coursesToIgnore, crosslistingmap = GrandAlpha.loadCrossListings(crossListingsFilename)
        
        schFile = open(filename, 'r')
        sch = {}
        previous_courseid = ''
        section_count = 1
        schFile.readline() # skip header
        for line in schFile:
            if len(line.strip()) > 0:
                linesplit = line.strip().split(',')
                
                # TODO: room numbers are only set in initialization file - what is imported here will be ignored
                # alternative is to attach a room to the schedule, so that different schedules could have different room numbers and this information would be available for comparison. This is probably better
                
                if detail:
                    if len(linesplit) < 14:
                        raise Exception('There does not appear to be enough data in the file to be used as a detailed schedule. Not enough data found on the following line:\n' + line)
                    timecode = linesplit[5].strip()
                else:
                    if len(linesplit) < 3:
                        raise Exception('There does not appear to be enough data in the file to be used as a simple schedule. Not enough data found on the following line:\n' + line)
                    timecode = linesplit[2].strip()
                
                if timecode.find(';') > 0:
                    raise ValueError(timecode + ' has multiple times listed. Perhaps this file is meant for initialization of the Grand Alpha, not as a valid schedule')
                
                registrar_crs_cde = linesplit[1].strip()
                crs_cde_elements = registrar_crs_cde.split(' ')
                courseid = crs_cde_elements[0] + crs_cde_elements[1]
                if courseid not in coursesToIgnore:
                    course_name = courseid
                    if courseid in self.course_list_multisection:
                        if courseid != previous_courseid: # the courses must be in order for this to work
                            section_count = 1
                        course_name += '-' + str(section_count)
                        section_count += 1
                    sch[course_name] = timecode
                    previous_courseid = courseid

        schFile.close()
        
        # for each faculty member, get all courses and test every combination for a conflict
        for facCourses in self.allFacCourses.allFacCourses:
            for i in range(len(facCourses.courses)):
                for j in range(i + 1, len(facCourses.courses)):
                    time1 = sch[facCourses.courses[i]]
                    if time1 not in self.validTimes:
                        raise ValueError(time1 + ' (for ' + facCourses.courses[i] + ') is not in the list of valid times')
                    time2 = sch[facCourses.courses[j]]
                    if time2 not in self.validTimes:
                        raise ValueError(time2 + ' (for ' + facCourses.courses[j] + ') is not in the list of valid times')
                    if self.doTimesConflict(time1, time2):
                        print('WARNING:', facCourses.name, 'has a conflict between', facCourses.courses[i], 'and', facCourses.courses[j], 'in the imported schedule.')
        
        return sch

    def importSchDetail(self, filename):
        return self.importSch(filename, True)
