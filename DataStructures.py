class FacultyCourses:
    def __init__(self, line):
        line = line.strip()
        elements = line.split(',')
        self.name = elements.pop(0)
        self.courses = elements.copy()
        firstchar = self.courses[0][0]
        # TODO: tie this to helper code that has been added
        if firstchar == 'C':
            secondchar = self.courses[0][1]
            if secondchar == 'S':
                self.dept = 'Computer Science'
            else:
                self.dept = 'Chemistry'
        elif firstchar == 'P':
            self.dept = 'Physics'
        elif firstchar == 'M' or firstchar == 'S' or firstchar == 'D':
            self.dept = 'Math'
        elif firstchar == 'I':
            self.dept = 'Computer Science'
        elif firstchar == 'B':
            self.dept = 'Biology'
        else:
            self.dept = 'Unknown'
            print('Unknown department for', self.name)
    
    def contains(self, course):
        return course in self.courses
    
    def print(self):
        print(self.name, 'in', self.dept, 'has courses ', end = '')
        for course in self.courses:
            print(course, ' ', end = '', sep = '')


class AllFacultyCourses:
    def __init__(self):
        self.allFacCourses = []
    
    def append(self, facCourses):
        self.allFacCourses.append(facCourses)
    
    def getFacCourses(self, name):
        if type(name) == int:
            return self.allFacCourses[name]
        elif type(name) == str:
            for facCourses in self.allFacCourses:
                if facCourses.name == name:
                    return facCourses
            return None
        return None
    
    def getFacByCourse(self, course):
        for facCourses in self.allFacCourses:
            if facCourses.contains(course):
                return facCourses
        return None
    
    def getFacNameByCourse(self, course):
        facCourses = self.getFacByCourse(course)
        return facCourses.name
    
    def getFacOtherCoursesByCourse(self, course):
        facCourses = self.getFacByCourse(course)
        courses = []
        for el in facCourses.courses:
            if el != course:
                courses.append(el)
        return courses
    
    def print(self):
        for facCourses in self.allFacCourses:
            facCourses.print()
            print()


class CourseTimes:
    def __init__(self, line):
        line = line.strip()
        elements = line.split(',')
        self.name = elements.pop(0)
        #self.maxsize = elements.pop(0)
        self.times = elements.copy()
    
    def contains(self, time):
        return time in self.times
    
    def isCourseNameMultiSection(name):
        return '-' in name
    
    def isCourseMultiSection(self):
        return CourseTimes.isCourseNameMultiSection(self.name)
    
    def getCourseNum(name):
        numstart = 1
        if name[numstart].isalpha():
            numstart += 1
        hyphenpos = name.find('-')
        if hyphenpos > 0:
            return name[numstart:hyphenpos]
        else:
            return name[numstart:]
    
    def getCourseSectionNum(name):
        hyphenpos = name.find('-')
        if hyphenpos > 0:
            return '0' + name[hyphenpos + 1]
        else:
            return '01'
    
    def getCourseDept(name):
        firstchar = name[0]
        if firstchar == 'C':
            secondchar = name[1]
            if secondchar == 'S':
                dept = 'Computer Science'
            else:
                dept = 'Chemistry'
        elif firstchar == 'P':
            secondchar = name[1]
            if secondchar == 'H':
                dept = 'Biology'
            else:
                dept = 'Physics'
        elif firstchar == 'M' or firstchar == 'S' or firstchar == 'D':
            dept = 'Math'
        elif firstchar == 'I':
            dept = 'Computer Science'
        elif firstchar == 'B':
            dept = 'Biology'
        else:
            dept = 'Unknown'
            print('Unknown department with code', firstchar)
        
        return dept
    
    def getCourseDeptCode(name):
        firstchar = name[0]
        if firstchar == 'C':
            secondchar = name[1]
            if secondchar == 'S':
                code = 'CSIS'
            else:
                code = 'CHEM'
        elif firstchar == 'P':
            secondchar = name[1]
            if secondchar == 'H':
                code = 'PHIL'
            else:
                code = 'PHYS'
        elif firstchar == 'M':
            code = 'MATH'
        elif firstchar == 'S':
            code = 'STAT'
        elif firstchar == 'D':
            code = 'DAST'
        elif firstchar == 'I':
            code = 'ISYS'
        elif firstchar == 'B':
            code = 'BIOL'
        else:
            code = 'Unknown'
            print('Unknown department for code', firstchar)
        
        return code
    
    def getDayTime(time):
        if time == 'MWF8':
            day = 'MWF'; start = '8:00AM'; end = '8:50AM'
        if time == 'MWF9':
            day = 'MWF'; start = '9:00AM'; end = '9:50AM'
        if time == 'MWF10:30':
            day = 'MWF'; start = '10:30AM'; end = '11:20AM'
        if time == 'MWF11:30':
            day = 'MWF'; start = '11:30AM'; end = '12:20PM'
        if time == 'MWF1':
            day = 'MWF'; start = '1:00PM'; end = '1:50PM'
        if time == 'MWF2:30':
            day = 'MWF'; start = '2:30PM'; end = '3:20PM'
        if time == 'MW1':
            day = 'MW'; start = '1:00PM'; end = '2:15PM'
        if time == 'MW2:30':
            day = 'MW'; start = '2:30PM'; end = '3:45PM'
        if time == 'M1-4':
            day = 'M'; start = '1:00PM'; end = '4:00PM'
        if time == 'M1-5':
            day = 'M'; start = '1:00PM'; end = '5:00PM'
        if time == 'W1-4':
            day = 'W'; start = '1:00PM'; end = '4:00PM'
        if time == 'W1-5':
            day = 'W'; start = '1:00PM'; end = '5:00PM'
        if time == 'TR8':
            day = 'TR'; start = '8:00AM'; end = '9:15AM'
        if time == 'TR10:30':
            day = 'TR'; start = '10:30AM'; end = '11:45AM'
        if time == 'TR1':
            day = 'TR'; start = '1:00PM'; end = '2:15PM'
        if time == 'TR2:30':
            day = 'TR'; start = '2:30PM'; end = '3:45PM'
        if time == 'T1-4':
            day = 'T'; start = '1:00PM'; end = '4:00PM'
        if time == 'T1-5':
            day = 'T'; start = '1:00PM'; end = '5:00PM'
        if time == 'R1-4':
            day = 'R'; start = '1:00PM'; end = '4:00PM'
        if time == 'R1-5':
            day = 'R'; start = '1:00PM'; end = '5:00PM'
        if time == 'MW4':
            day = 'MW'; start = '4:00PM'; end = '5:15PM'
        if time == 'MWF10:30-12:20':
            day = 'MWF'; start = '10:30AM'; end = '12:20PM'
        if time == 'F1':
            day = 'F'; start = '1:00PM'; end = '1:50PM'
        if time == 'F1:30':
            day = 'F'; start = '1:30PM'; end = '3:30PM'
        if time == 'F2':
            day = 'F'; start = '2:00PM'; end = '2:50PM'
        if time == 'M6':
            day = 'M'; start = '6:00PM'; end = '?'
        if time == 'T6':
            day = 'T'; start = '6:00PM'; end = '?'
        if time == 'W6':
            day = 'W'; start = '6:00PM'; end = '?'
        if time == 'W8':
            day = 'W'; start = '8:00AM'; end = '8:50AM'
        if time == 'T4':
            day = 'T'; start = '4:00PM'; end = '4:50PM'
        
        return day, start, end
    
    def print(self):
        print(self.name, 'has available times ', end = '')
        for time in self.times:
            print(time, ' ', end = '', sep = '')


class AllCourseTimes:
    def __init__(self):
        self.allCourseTimes = []
    
    def append(self, courseTimes):
        self.allCourseTimes.append(courseTimes)
    
    def getAllCourses(self):
        return [courseTimes.name for courseTimes in self.allCourseTimes]
    
    def getCourseTimes(self, name):
        if type(name) == int:
            return self.allCourseTimes[name]
        elif type(name) == str:
            for courseTimes in self.allCourseTimes:
                if courseTimes.name == name:
                    return courseTimes
            return None
        return None
    
    def print(self):
        for courseTimes in self.allCourseTimes:
            courseTimes.print()
            print()


class Conflict:
    def __init__(self, course1, course2, priority):
        if course1 > course2:
            course1, course2 = course2, course1
        self.course1 = course1
        self.course2 = course2
        self.priority = int(priority)
    
    def print(self):
        print(self.course1, 'and', self.course2, 'conflict with priority', self.priority)


class AllConflicts:
    def __init__(self):
        self.allConflicts = []
    
    def add(self, course1, course2, priority):
        conflict = self.getConflict(course1, course2)
        if conflict == None:
            self.allConflicts.append(Conflict(course1, course2, priority))
        else:
            conflict.priority += int(priority)

    def getConflict(self, course1, course2):
        if course1 > course2:
            course1, course2 = course2, course1
        for conflict in self.allConflicts:
            if conflict.course1 == course1 and conflict.course2 == course2:
                return conflict
        return None
    
    def getPenalty(self, course1, course2):
        # for tests that involve courses that have more than one section, assume no conflicts
        if CourseTimes.isCourseNameMultiSection(course1) or CourseTimes.isCourseNameMultiSection(course2):
            return 0
        
        if course1 > course2:
            course1, course2 = course2, course1
        for conflict in self.allConflicts:
            if course1 == conflict.course1 and course2 == conflict.course2:
                return conflict.priority
        return 0
    
    def print(self):
        for conflict in self.allConflicts:
            conflict.print()


class TimeConflict:
    def __init__(self, time1, time2):
        if time1 > time2:
            time1, time2 = time2, time1
        self.time1 = time1
        self.time2 = time2
    
    def print(self):
        print(self.time1, 'and', self.time2, 'conflict')


class StudentCourses:
    def __init__(self, line):
        line = line.strip()
        elements = line.split(',')
        self.name = elements.pop(0)
        self.priority = int(elements.pop(0))
        self.courses = elements.copy()
    
    def print(self):
        print(self.name, 'with priority', self.priority, 'has courses ', end = '')
        for course in self.courses:
            print(course, ' ', end = '', sep = '')
        print()
