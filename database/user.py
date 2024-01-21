

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


class Problem :
	def __init__(self) -> None:
		self.id = 0
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


class Topic :
	def __init__(self) -> None:
		self.id = 0
		self.topicName = ""
		self.createdAt = ""
		self.updatedAt = ""
		self.problems = []

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

class UserMonthlyObject :
	def __init__(self) -> None:
		self.id = 0
		self.createdAt = ""
		self.updatedAt = ""
		self.userId = 0
		self.scoreEarned = 0
		self.firstDayOfMonth = 0
		self.user = User()     

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

class DiscordQuizAnswer :
	def __init__(self) -> None:
		self.id            = 0         
		self.createdAt     = ""    
		self.updatedAt     = ""    
		self.answer        = ""
		self.discordQuizId = 0
		self.discordQuiz = DiscordQuiz()

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