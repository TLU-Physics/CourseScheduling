from math import sqrt,exp
from random import random,choice

from DataStructures import *

class GrandAlpha:
    def __init__(self, facCourseFilename, courseTimesFilename, conflictsFilename, timeConflictsFilename):
        # load the valid time labels (for error checking)
        validTimesFilename = 'ValidTimes.txt'
        validTimesFile = open(validTimesFilename, 'r')
        self.validTimes = set()
        for line in validTimesFile:
            if len(line.strip()) > 0:
                self.validTimes.add(line.strip())
        
        # load the information about what possible times each course can be taught at
        courseTimesFile = open(courseTimesFilename, 'r')
        self.allCourseTimes = AllCourseTimes()
        for line in courseTimesFile:
            if len(line.strip()) > 0:
                courseTimes = CourseTimes(line)
                for t in courseTimes.times:
                    if t not in self.validTimes:
                        raise ValueError(t + ' (for ' + courseTimes.name + ') is not in the list of valid times')
                self.allCourseTimes.append(courseTimes)

        courseTimesFile.close()
        
        allCoursesList = self.allCourseTimes.getAllCourses()
        
        # load the information about what courses faculty are teaching
        facCourseFile = open(facCourseFilename, 'r')
        self.allFacCourses = AllFacultyCourses() # this will be the list of faculty schedules
        for line in facCourseFile:
            if len(line.strip()) > 0:
                facCourses = FacultyCourses(line)
                for course in facCourses.courses:
                    if course not in allCoursesList:
                        print('The course', course, 'is not in the master list of courses')
                        raise Exception
                self.allFacCourses.append(facCourses)

        facCourseFile.close()
        
        # load the information about the course conflicts that exist that the new
        # schedule must adapt to
        conflictsFile = open(conflictsFilename, 'r')
        self.allConflicts = AllConflicts()
        for line in conflictsFile:
            if len(line.strip()) > 0:
                els = line.strip().split(',')
                if els[0] not in allCoursesList:
                    print('The course', els[0], 'is not in the master list of courses')
                    raise Exception
                if els[1] not in allCoursesList:
                    print('The course', els[1], 'is not in the master list of courses')
                    raise Exception
                self.allConflicts.append(els[0], els[1], int(els[2]))

        conflictsFile.close()

        # load the information about the time conflicts that exist
        # this defines times that should be considered overlapping
        timeConflictsFile = open(timeConflictsFilename, 'r')
        self.allTimeConflicts = []
        for line in timeConflictsFile:
            if len(line.strip()) > 0:
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
                print(tryCount)
                return sch

    def accumulatePenalties(self, sch):
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
                    totalPenalties += self.allConflicts.getPenalty(courses[i], courses[j])
        
        # for each 2 times that overlap, find all courses in each of the 2 groups
        # and test every possible pair
        for timeConflict in self.allTimeConflicts:
            if timeConflict.time1 in inv_sch and timeConflict.time2 in inv_sch:
                for course1 in inv_sch[timeConflict.time1]:
                    for course2 in inv_sch[timeConflict.time2]:
                        totalPenalties += self.allConflicts.getPenalty(course1, course2)
        
        return totalPenalties
    
    def anneal(self, sch):
        Tmax = 1000.0
        Tmin = 0.1
        tau = 1e4

        t = 0
        T = Tmax
        penalties = self.accumulatePenalties(sch)
        while T > Tmin:
            
            # show progress
            if t % 100 == 0:
                print('Steps taken:', t)

            # Cooling
            T = Tmax*exp(-t/tau)

            schnew = self.StepSchedule(sch)
            penaltiesnew = self.accumulatePenalties(sch)
            deltaPenalties = penaltiesnew - penalties

            # accept the new sch according to Boltzmann factor
            if random() < exp(-deltaPenalties / T):
                sch = schnew
                penalties = penaltiesnew
            
            t += 1
        
        return sch

    def summary(self, sch):
        penalties = self.accumulatePenalties(sch)
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
                s = facCourses.name + ', ' + course + ', ' + sch[course] + '\n'
                outfile.write(s)
        
        outfile.close()
    
    def importSch(self, filename):
        schFile = open(filename, 'r')
        sch = {}
        for line in schFile:
            if len(line.strip()) > 0:
                linesplit = line.strip().split(',')
                sch[linesplit[1].strip()] = linesplit[2].strip()

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
