from typing import NamedTuple

class FacultyCourses:
    def __init__(self, line, dept):
        line = line.strip()
        elements = line.split(',')
        self.name = elements.pop(0)
        self.courses = elements.copy()
        self.dept = dept
        
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
        print('There are no faculty assigned to teach ', course, '!')
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
    
    def getFacultyCoursesItemByName(self, facultyName):
        for facCourses in self.allFacCourses:
            if facCourses.name == facultyName:
                return facCourses
        return None
    
    def print(self):
        for facCourses in self.allFacCourses:
            facCourses.print()
            print()


class TimeDetail(NamedTuple):
    day: str
    start: str
    end: str


class CourseTimes:
    def __init__(self, category, name, hours, cde, timecode, building, room, cap):
        self.category = category.strip()
        self.name = name.strip()
        self.hours = hours.strip()
        self.cde = cde.strip()
        self.building = building.strip()
        self.room = room.strip()
        self.capacity = cap.strip()
        self.times = timecode.strip().split(';')
    
    def contains(self, time):
        return time in self.times
    
    def isCourseNameMultiSection(name):
        return '-' in name
    
    def isCourseMultiSection(self):
        return CourseTimes.isCourseNameMultiSection(self.name)
    
    def getCourseNum(name):
        numstart = 4
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
    
    def getCourseDeptCode(name):
        code = name[0:4]
        
        return code
    
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
        
    def getCourseDept(self, name):
        if type(name) == int:
            return self.allCourseTimes[name].category
        elif type(name) == str:
            for courseTimes in self.allCourseTimes:
                if courseTimes.name == name:
                    return courseTimes.category
                    
            # handle cross listings, which are not in the original list
            code = CourseTimes.getCourseDeptCode(name)
            if code == 'CSCI' or code == 'ISYS':
                dept = 'Csis'
            elif code == 'CHEM' or code == 'NSCI':
                dept = 'Chemistry'
            elif code == 'PHYS':
                dept = 'Physics'
            elif code == 'MATH' or code == 'STAT' or code == 'DAST' or code == 'DAIC' or code == 'DASC':
                dept = 'Math'
            elif code == 'BIOL' or code == 'ENVS':
                dept = 'Biology'
            elif code == 'FREX' or code == 'PHIL':
                dept = 'Biology'
            else:
                dept = 'Unknown'
                print('Unknown department with code', code)
            
            return dept
        return None
        
    def getCourseInfo(self, name):
        if type(name) == int:
            return self.allCourseTimes[name].category, self.allCourseTimes[name].hours, self.allCourseTimes[name].cde, self.allCourseTimes[name].building, self.allCourseTimes[name].room, self.allCourseTimes[name].capacity
        elif type(name) == str:
            for courseTimes in self.allCourseTimes:
                if courseTimes.name == name:
                    return courseTimes.category, courseTimes.hours, courseTimes.cde, courseTimes.building, courseTimes.room, courseTimes.capacity
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
    
    def add(self, course1, course2, priority = 5):
        conflict = self.getConflict(course1, course2)
        if conflict == None:
            self.allConflicts.append(Conflict(course1, course2, priority))
        else:
            if conflict.priority < int(priority):
                conflict.priority = int(priority)
            #else:
                #print('Trying to add the conflict between', course1, 'and', course2, 'again. Ignoring.')
            #conflict.priority += int(priority)

    def addCluster(self, courseList, priority = 5):
        numCourses = len(courseList)
        for i in range(numCourses):
            for j in range(i + 1, numCourses):
                self.add(courseList[i], courseList[j], priority)

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
