import numpy as np
from copy import deepcopy
import json
from datetime import datetime
import compress_json


class Connect4():

    def __init__(self)  -> None:
        self.cols = 5
        self.rows = 4
        self.colored_cells = {1: 0, 2: 0}
        self.board = np.zeros((self.rows, self.cols), dtype="int8")
        self.cells = self.cols * self.rows
        self.freecells = self.cells

    def reset(self)  -> None:
        self.__init__()

    def get_player(self) -> int :

        ''' Return Current 
        1 -> Red
        2 -> Yellow
        '''
        return int(self.colored_cells[1] > self.colored_cells[2]) + 1

    def update_player_cells(self) -> None:
        ''' Updates number of cells of each player '''
        self.colored_cells[self.get_player()] += 1
    
    def update_free_cells(self)  -> None:
        ''' Decreases number of free cells '''
        self.freecells -= 1

    def col_availability(self, col) -> bool :
        ''' Check if col has free space'''
        return 0 in self.board[:, col]

    def available_moves(self) :

        ''' Get all available moves '''
        actions = []

        order = np.arange(self.cols)
        np.random.shuffle(order)

        for c in order :
            if self.col_availability(c) :
                r = self.available_row(c)
                actions.append( (r,c) )

        return actions
                

    def available_row(self,col) -> int:

        ''' Returns corresponding row coordinate'''

        col_items = self.board[:, col]
        for i in range(1, self.rows+1):
            if col_items[-i] == 0:
                return -i

    def move(self,action) -> bool:
        '''Gets corresponding cell and updates the game accordingly '''
        row,col = action
        self.board[row,col] = self.get_player()
        self.update_player_cells()
        self.update_free_cells()
        return True

    def win(self) -> int:
        
        def partition_checker(chunk) :
            for j in range(chunk.size-3):
                partition = chunk[j:j+4]
                if len(set(partition)) == 1 and 0 not in partition:
                    return partition[0]
        
        board_flipped = np.fliplr(self.board.copy())

        for i in range(-self.cols+3, self.cols-3):
            diagonal_1 = self.board.diagonal(i)
            result_1 = partition_checker(diagonal_1)
            if result_1 : return result_1

            diagonal_2 = board_flipped.diagonal(i)
            result_2 = partition_checker(diagonal_2)
            if result_2 : return result_2

        for i in range(self.rows) :
            row = self.board[i,:]
            result = partition_checker(row)
            if result : return result

        for i in range(self.cols) :
            col = self.board[:,i]
            result = partition_checker(col)
            if result : return result

        return 0

    def terminal_state(self) -> int:
        '''
        -1 -> Draw \n
        1 -> Red win \n
        2 -> Yellow win \n
        0 -> Ongoing     
        '''
        
        winner = self.win()

        if winner :
            return winner
        
        if self.freecells == 0 :
            return -1
        
        return 0
    
    def copy(self) :
        return deepcopy(self)

    def get_state(self) :
        return tuple(self.board.flatten())
    
class AI() :

    def __init__(self) :
        # Knowledge base ( {player state action : })
        self.q = dict()
        self.alpha = 0.7
        self.gamma = 0.55
        
    def next_move(self, game : Connect4, training = False ) :

        available_actions = list(game.available_moves())
        player : int = game.get_player()
        state = game.get_state()


        if not training :
            percentage = self.remaining_percentage(game)
            chance = 1/70 * percentage - 1/70 * 30
            move_chosen = self.game_move(available_actions,player,state,np.random.random() < chance)

        else :
            action_weights = self.categorize(available_actions,player,state)
            normalized_weights = self.normalize(action_weights)
            weights  = list(normalized_weights.keys())
            values = list(normalized_weights.values())
            row_chosen = int(np.random.choice(np.arange(0,len(weights)),size=1,p=weights))
            move_chosen = values[row_chosen][np.random.randint(0,len(values[row_chosen]))]
            
        return move_chosen
    
    def remaining_percentage(self,game : Connect4) :
        
        return 100 - ( ((game.cols * game.rows - game.freecells)/(game.cols * game.rows)) * 100)

    def game_move(self,actions,player,state,lenient) :
        moves_chosen = [actions[0]]
        best_reward = self.get_old_reward(moves_chosen[0],state,player)

        for action in actions :
            action_reward = self.get_old_reward(action,state,player)
            print(f"Action : {action} Reward : {action_reward}")

            if abs(action_reward-best_reward) <= 0.2 and lenient and moves_chosen[0] != action:
                moves_chosen.append(action)
            elif best_reward < action_reward :
                best_reward = action_reward
                moves_chosen = [action]
        move_chosen = moves_chosen[np.random.randint(0,len(moves_chosen))]
        print(f"Action_Chosen : {move_chosen} reward : {self.get_old_reward(move_chosen,state,player)}")
        return move_chosen
    
    def categorize(self,actions : list, player,state) -> dict:

        action_weights = {
            0.35 : [],
            0.25 : [],
            0.15 : [],
            0.08 : [],
            0.06 : [],
            0.05 : [],
            0.04 : [],
            0.02 : []
        }
        
        for action in actions :
            reward = self.get_old_reward(action,state,player)

            if reward>2.25 :
                action_weights[0.35].append(action)
            elif 2.25>=reward>1.5 :
                action_weights[0.25].append(action)
            elif 1.5>=reward>0.75 :
                action_weights[0.15].append(action)
            elif 0.75>=reward>0 :
                action_weights[0.08].append(action)
            elif 0>=reward> -0.75 :
                action_weights[0.06].append(action)
            elif -0.75>=reward>-1.5 :
                action_weights[0.05].append(action)
            elif -1.5>=reward>-2.25 :
                action_weights[0.04].append(action)
            elif -2.25>=reward :
                action_weights[0.02].append(action)
        
        return action_weights
        
    def normalize(self,action_weights : dict) -> dict:
        
        summation = 0
        updated_action_weights = deepcopy(action_weights)

        for weight,actions in action_weights.items() :
            if len(actions) != 0 :
                summation += weight
            else :
                del updated_action_weights[weight]
        k = 1/summation

        normalized_weights = dict()

        for weight, actions in updated_action_weights.items() :
            normalized_weights[weight*k] = actions
        
        return normalized_weights

    def update(self,action : tuple ,old_game : Connect4, new_game : Connect4,new_reward : int,player :int) : 
        old_reward = self.get_old_reward(action,old_game.get_state(),player)
        future_reward = self.get_future_reward(new_game,player)
        final_reward = self.evaluate(new_reward,old_reward,future_reward)
        self.q[str((player,old_game.get_state(),action))] = final_reward

    def evaluate(self,new_reward:int,old_reward:int,future_rewards:int) -> float :

        final_reward = old_reward + self.alpha * (new_reward + self.gamma * future_rewards - old_reward)
        return final_reward
    
    def get_future_reward(self,new_game : Connect4,player : int) :
        
        if new_game.terminal_state() :
            return 0
                
        available_actions = new_game.available_moves()
        rewards = []

        for action in available_actions :
            rewards.append(self.get_old_reward(action,new_game.get_state(),player)) 

        return max(rewards)

    def get_old_reward(self,action : tuple ,state : tuple ,player : int) -> int:
        return self.q.get(str((player,state,action)),0.5)
    
    def train(self,n : int ) :
        
        for i in range(1,n+1) :

            game = Connect4()
            previous = {
                1 : {"state" : None, "action" : None},
                2 : {"state" : None, "action" : None}
            }
            on_going = True

            while on_going :

                action = self.next_move(game,True)
                past_player = game.get_player()

                old_game = game.copy()

                previous[past_player]["state"] = old_game
                previous[past_player]["action"] = action

                game.move(action)
                curr_player = game.get_player()

                status = game.terminal_state()

                if status == -1  :
                    self.update(previous[curr_player]["action"],previous[curr_player]["state"],game,-1,curr_player)
                    self.update(action,old_game,game,-1,past_player)
                    on_going = False
                elif status == 2 or status == 1 :
                    self.update(action,old_game,game,3,past_player)
                    self.update(previous[curr_player]["action"],previous[curr_player]["state"],game,-3,curr_player)
                    on_going = False
                elif previous[curr_player]["action"] is not None :
                    self.update(previous[curr_player]["action"],previous[curr_player]["state"],game,0,curr_player)

            if i%10000 == 0 :
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print(f"{current_time} : Completed {i} trainings")

            if i%10000 == 0 :
                self.export()
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print(f"{current_time} : Exported at {i}")
        self.export()
        self.export(True)

    def export(self,final=False) :

        if final :
            compress_json.dump(self.q,"4x5.gz")
            return
            
        data = json.dumps(self.q,indent=4)
        with open("4x5.json", "w") as outfile:
            outfile.write(data)
    
    def populate(self,compressed=False) :

        print("Importing ...")
        if compressed :
            self.q = compress_json.load("4x5.gz")
        else :
            with open("4x5.json") as infile :
                self.q = json.load(infile)
        print("Import done")

        print(self.q["(2, (0, 1, 0, 2, 0, 2, 2, 0, 1, 2, 1, 2, 0, 1, 1, 1, 2, 1, 1, 2), (-4, 4))"] == 0.08698737399252718)

new_ai = AI()
new_ai.populate(True)
