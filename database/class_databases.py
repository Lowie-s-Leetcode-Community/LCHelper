

class User :
	def __init__(self):
		self.id = 0
		self.discord_id = "000"
		self.lc_username = "abcxyz"
		self.created_at = ""
		self.updated_at = ""
		self.most_recent_sub_id = 0
		self.user_daily_objects = []
		self.user_monthly_objects = []
		self.user_solved_problems = []

	def get_discord_id(self):
		return self.discord_id
	
	def get_lc_username(self):
		return self.lc_username
	
	def get_created_at(self): 
		return self.updated_at
	
	def get_most_recent_sub_id(self): 
		return self.most_recent_sub_id
	
	def get_user_daily_objects(self): 
		return self.user_daily_objects
	
	def get_user_monthly_objects(self): 
		return self.user_monthly_objects
	
	def get_user_solved_problems(self):
		return self.user_solved_problems


class Problem :
	def __init__(self) -> None:
		self.id = 0
		self.createdAt = ""
		self.updatedAt = ""
		self.title = ""
		self.titleSlug  = ""
		self.difficulty  = ""
		self.isPremium  = False
		self.dailyObjects = []
		self.userSolvedProblems = []
		self.missions = []
		self.topics = []

	def get_Id(self) :
		return self.id
	def get_createdAt(self) :
		return self.createdAt
	def get_updatedAt(self) :
		return self.updatedAt
	def get_title(self) :
		return self.title
	def get_titleSlug(self) :
		return self.titleSlug
	def get_difficulty(self) :
		return self.difficulty
	def get_isPremium(self) :
		return self.isPremium
	def get_dailyObjects(self) :
		return self.dailyObjects
	def get_userSolvedProblems(self) :
		return self.userSolvedProblems
	def get_missions(self) :
		return self.missions
	def get_topics(self) :
		return self.topics


class UserSolvedProblem :
	def __init__(self) -> None:
		self.id = 0
		self.submissionId = 0
		self.problemId   = 0
		self.userId       = 0
		self.createdAt    = ""
		self.updatedAt    = ""
		self.problem      = Problem()
		self.user   = User()

	def get_id(self) :
		return self.id
	def get_submissionI(self) :
		return self.submissionId
	def get_problemId (self) :
		return self.problemId  
	def get_userId     (self) :
		return self.userId      
	def get_createdAt   (self) :
		return self.createdAt   
	def get_updatedAt   (self) :
		return self.updatedAt   
	def get_problem(self) :
		return self.problem 
	def get_user(self) :
		return self.user


class Topic :
	def __init__(self) -> None:
		self.id = 0
		self.topicName = ""
		self.createdAt = ""
		self.updatedAt = ""
		self.problems = []

	def get_id(self) :
		return self.id

	def get_topicName (self) :
		return self.topicName 

	def get_createdAt(self) :
		return self.createdAt

	def get_updatedAt(self) :
		return self.updatedAt

	def get_problems(self) :
		return self.problems


class DailyObject :
	def __init__(self) -> None:
		self.id = 0
		self.createdAt = ""
		self.updatedAt = ""              
		self.problemId = 0
		self.isToday = False    
		self.generatedDate = ""
		self.problem = Problem()
		self.userDailyObjects = []

	def get_id (self) :
		return self.id
	def get_created_at(self):
		return self.createdAt
	def get_updatedAt(self) :
		return self.updatedAt
	def get_problemId(self):
		return self.problemId
	def get_isToday(self) :
		return self.isToday
	def get_generateDate(self):
		return self.generatedDate 
	def get_problem (self) :
		return self.problem
	def get_user_daily_objects(self):
		return self.userDailyObjects

class UserDailyObject :
	def __init__(self):
		self.id = 0
		self.createdAt = ""
		self.updatedAt = ""
		self.userId = 0
		self.dailyObjectId = 0

		self.solvedDaily = 0        
		self.solvedEasy = 0
		self.solvedMedium  = 0
		self.solvedHard  = 0
		self.scoreEarned  = 0
		self.scoreGacha  = 0

		self.dailyObject  = DailyObject()
		self.user  = User()

	def get_id(self):
		return self.id
	def get_createdAt(self):
		return self.createdAt
	def get_updatedAt(self):
		return self.updatedAt
	def get_userId(self):
		return self.userId
	def get_dailyObjectId(self):
		return self.dailyObjectId

	def get_solvedDaily(self):
		return self.solvedDaily
	def get_solvedEasy(self):
		return self.solvedEasy
	def get_solvedMedium(self):
		return self.solvedMedium
	def get_solvedHard(self):
		return self.solvedHard
	def get_scoreEarned(self):
		return self.scoreEarned
	def get_scoreGacha(self):
		return self.scoreGacha

	def get_dailyObject(self):
		return self.dailyObject
	def get_user(self):
		return self.user

class UserMonthlyObject :
	def __init__(self) -> None:
		self.id = 0
		self.createdAt = ""
		self.updatedAt = ""
		self.userId = 0
		self.scoreEarned = 0
		self.firstDayOfMonth = 0
		self.user = User()

	def get_id(self) :
		return self.id
	def get_createdAt(self) :
		return self.createdAt
	def get_updatedAt(self) :
		return self.updatedAt
	def get_userId(self) :
		return self.userId
	def get_scoreEarned(self) :
		return self.scoreEarned
	def get_firstDayOfMonth(self) :
		return self.firstDayOfMonth
	def get_user(self) :
		return self.user

class Mission :
	def __init__(self) -> None:
		self.id = 0
		self.name = ""
		self.description = ""
		self.createdAt      = ""  
		self.updatedAt      = ""  
		self.isHidden       = False
		self.rewardImageURL = ""
		self.problems = []

	def get_id(self):
		return self.id
	def get_name(self):
		return self.name
	def get_description(self):
		return self.description
	def get_createdAt(self):
		return self.createdAt
	def get_updatedAt(self):
		return self.updatedAt
	def get_isHidden(self):
		return self.isHidden
	def get_rewardImageURL(self):
		return self.rewardImageURL
	def get_problems(self):
		return self.problems

class DiscordQuiz :
	def __init__(self) -> None:
		self.id                = 0                 
		self.createdAt         = ""            
		self.updatedAt         = ""            
		self.category          = ""
		self.question          = ""
		self.difficulty        = ""
		self.correctAnswerId   = 0
		self.discordQuizAnswer = []

	def get_id(self):
		return self.id
	def get_createdAt(self):
		return self.createdAt
	def get_updatedAt(self):
		return self.updatedAt
	def get_category(self):
		return self.category
	def get_question(self):
		return self.question
	def get_difficulty(self):
		return self.difficulty
	def get_correctAnswerId(self):
		return self.correctAnswerId
	def get_discordQuizAnswer(self):
		return self.discordQuizAnswer

class DiscordQuizAnswer :
	def __init__(self) -> None:
		self.id            = 0         
		self.createdAt     = ""    
		self.updatedAt     = ""    
		self.answer        = ""
		self.discordQuizId = 0
		self.discordQuiz = DiscordQuiz()

	def get_id(self):
		return self.id
	def get_createdAt(self):
		return self.createdAt
	def get_updatedAt(self):
		return self.updatedAt
	def get_answer(self):
		return self.answer
	def get_discordQuizId(self):
		return self.discordQuizId
	def get_discordQuiz(self):
		return self.discordQuiz

class SystemConfiguration :
	def __init__(self):
		self.id                   = 0 
		self.serverId             = 0
		self.verifiedRoleId       = 0
		self.trackingChannelId    = 0
		self.scoreLogChannelId    = 0
		self.dailyThreadChannelId = 0
		self.lastDailyCheck       = ""
		self.feedbackChannelId    = 0
		self.qaChannelId          = 0
		self.eventChannelId       = 0
		self.timeBeforeKick       = 0
		self.unverifiedRoleId     = 0
		self.backupChannelId      = 0

	def get_id(self):
		return self.id
	def get_serverId(self):
		return self.serverId
	def get_verifiedRoleId(self):
		return self.verifiedRoleId
	def get_trackingChannelId(self):
		return self.trackingChannelId
	def get_scoreLogChannelId(self):
		return self.scoreLogChannelId
	def get_dailyThreadChannelId(self):
		return self.dailyThreadChannelId
	def get_lastDailyCheck(self):
		return self.lastDailyCheck
	def get_feedbackChannelId(self):
		return self.feedbackChannelId
	def get_qaChannelId(self):
		return self.qaChannelId
	def get_eventChannelId(self):
		return self.eventChannelId
	def get_timeBeforeKick(self):
		return self.timeBeforeKick
	def get_unverifiedRoleId(self):
		return self.unverifiedRoleId
	def get_backupChannelId(self):
		return self.backupChannelId