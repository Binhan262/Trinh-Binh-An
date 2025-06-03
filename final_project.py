import random
import math
def solve():
    #Read the input values
    N,M,K = map(int, input().split())
    a,b,c,d,e,f=map(int,input().split())
    s=[]
    for i in range(N):
        row = list(map(int, input().split()))
        s.append(row)
    g=[]
    for i in range(N):
        row = list(map(int, input().split()))
        g.append(row)
    t=list(map(int, input().split()))
    t=[x-1 for x in t] 
    
    #Check if a solution is feasible
    def is_feasible(x,y):
        committee_thesis=[[] for  i in range(K)]
        committee_teachers=[[] for i in range(K)]
        #Distribute thesis and teachers to committees
        for i in range(N):
            if 0<=x[i]<K:
                committee_thesis[x[i]].append(i)
        for i in range(M):
            if 0<=y[i]<K:
                committee_teachers[y[i]].append(i)
        for k in range(K):
            #Size constraints
            if len(committee_thesis[k])<a or len(committee_teachers[k])>b:
                return False                
            if len(committee_teachers[k])<c or len(committee_thesis[k])>d:
                return False   
            #Advisors constraints
            for thesis in committee_thesis[k]:
                advisor=t[thesis]
                if advisor in committee_teachers[k]:
                    return False
            #Similarity constraints
            for i in range(len(committee_thesis[k])):
                for j in range(i+1, len(committee_thesis[k])):
                    if s[committee_thesis[k][i]][committee_thesis[k][j]]<e:
                        return False    
            for thesis in committee_thesis[k]:
                for teacher in committee_teachers[k]:
                    if g[teacher][thesis]<f:
                        return False    
        return True
    
    #Caculate the objective value
    def calculate_objective(x,y):
        committee_thesis=[[] for  i in range(K)]
        committee_teachers=[[] for i in range(K)]
        #Distribute thesis and teachers to committees
        for i in range(N):
            if 0<=x[i]<K:
                committee_thesis[x[i]].append(i)
        for i in range(M):
            if 0<=y[i]<K:
                committee_teachers[y[i]].append(i)
        objective_value=0
        for k in range(K):
            #Similarity between thesis
            for i in range(len(committee_thesis[k])):
                for j in range(i+1, len(committee_thesis[k])):
                    objective_value+=s[committee_thesis[k][i]][committee_thesis[k][j]]
            #Similarity between thesis and teachers
            for thesis in committee_thesis[k]:
                for teacher in committee_teachers[k]:
                    objective_value+=g[teacher][thesis]
        return objective_value
    
    #Assign thesis greedy while balancing between size constraint and similarity 
    def assign_thesis_greedy(thesis_list,committee_students, x, exclude_committee=set()):
        for thesis in thesis_list:
            best_committee = -1
            best_value = -math.inf
            for k in range(K):
                # Check if the committee is excluded or if it already has enough thesis
                if k in exclude_committee or len(committee_students[k]) >= b:
                    continue
                value = 0
                valid = True
                for other_thesis in committee_students[k]:
                    if s[thesis][other_thesis] < e:
                        valid = False  # Similarity violation
                        break
                    value += s[thesis][other_thesis]
                # Balance with the size constraint (When <b/2 prefer size, >b/2 prefer similarity)
                value += (b - len(committee_students[k])) * 10
                # Choose the best committee to assign the thesis
                if valid and value > best_value:
                    best_value = value
                    best_committee = k
            # If cannot find a valid committee, assign to the one with the least thesis
            if best_committee == -1:
                available_committee = [k for k in range(K) if k not in exclude_committee and len(committee_students[k]) < b]
                if available_committee:
                    best_committee = min(available_committee, key=lambda k: len(committee_students[k]))
            # Assign the thesis to the best committee
            if best_committee != -1:
                committee_students[best_committee].append(thesis)
                x[thesis] = best_committee
    
    #Assign a teacher greedy while balancing between similarity and avoid violating constraints
    def assign_teachers_greedy(teacher,committee_students,committee_teachers,y):
        best_committee=-1
        best_value=-math.inf
        for k in range(K):
            # Check if the committee violate constraints
            if len(committee_teachers[k]) >= d:
                continue
            if any(t[thesis]==teacher for thesis in committee_students[k]):
                continue #Advisor violation
            value=0
            valid=True
            for thesis in committee_students[k]:
                if g[teacher][thesis] < f:
                    valid = False # Similarity violation
                    break
                value += g[teacher][thesis]
            # Balance with the size constraint
            value += (d-len(committee_teachers[k]))*20 #Make it large enough to balance betweem size and similarity
            #Choose the best committee to assign the teacher
            if valid and value > best_value:
                best_value = value
                best_committee = k
        #Assign the teacher to the best committee
        if best_committee != -1:
            committee_teachers[best_committee].append(teacher)
            y[teacher] = best_committee
        return best_committee
    
    #Ensure that each committee has minimum size while not violate hard constraints
    def ensure_minimum_requirements(committee_students,committee_teachers,x,y):
        #Ensure enough thesis in each committee by adding from the biggest committee except itself
        for k in range(K):
            while len(committee_students[k])<a:
                biggest=max(range(K),key=lambda i:len(committee_students[i]) if  i!=k else 0)                           
                if len(committee_students[biggest]) > a:
                    found_thesis = None
                    # Find a thesis that can be moved without violating hard constraints
                    for thesis in committee_students[biggest]:
                        if t[thesis] not in committee_teachers[k]:
                            found_thesis = thesis
                            break
                    # Move the thesis if found one that can be moved
                    if found_thesis is not None:
                        committee_students[biggest].remove(found_thesis)
                        committee_students[k].append(found_thesis)
                        x[found_thesis] = k
                else:
                    break # No thesis can be moved from this committee, try next biggest  
        #Ensure enough teacher
        for k in range(K):
            while len(committee_teachers[k])<c:
                assigned=False
                # Find a teacher that has not assigned first
                for teacher in range(M):
                    if y[teacher] == -1 and not any(t[thesis]==teacher for thesis in committee_students[k]):
                        assigned = True
                        committee_teachers[k].append(teacher)
                        y[teacher] = k
                        break     
                #Move from other committee if no teacher available
                if not assigned:
                    for other_k in range(K):
                        if other_k!=k and len(committee_teachers[other_k]) > c:
                            for teacher in committee_teachers[other_k]:
                                if not any(t[thesis]==teacher for thesis in committee_students[k]):
                                    committee_teachers[other_k].remove(teacher)
                                    committee_teachers[k].append(teacher)
                                    y[teacher] = k
                                    assigned = True
                                    break 
                            if assigned:
                                break #Done with this committee, break the loop  
                if not assigned:
                    break # No teacher can be moved to this committee, try next committee           
                
    #Initialize the solution by greedy
    def greedy():
        committee_students = [[] for k in range(K)]
        committee_teachers = [[] for k in range(K)]
        x = [-1] * N
        y = [-1] * M
        #Assign thesis and teacher to committees
        thesis_order = list(range(N))   
        random.shuffle(thesis_order)
        assign_thesis_greedy(thesis_order, committee_students, x)
        teacher_order = list(range(M))
        random.shuffle(teacher_order)
        for teacher in teacher_order:
            assign_teachers_greedy(teacher, committee_students, committee_teachers, y)
        #If have unassigned teachers cause total case of t[i]=teacher>=k
        unassigned_teachers = [teacher for teacher in range(M) if y[teacher] == -1]
        if unassigned_teachers:
            #Reset and apply new method
            x = [-1] * N
            y = [-1] * M
            committee_students = [[] for k in range(K)]
            committee_teachers = [[] for k in range(K)]
            #Put first teacher in committee 0
            committee_teachers[0].append(unassigned_teachers[0])
            y[unassigned_teachers[0]] = 0
            #Assign thesis that this teacher is advisor to other committees
            supervised_thesis = [i for i in range(N) if t[i]==unassigned_teachers[0]]
            assign_thesis_greedy(supervised_thesis, committee_students, x,{0})
            #Assign other teachers to committees and their thesis
            for teacher in unassigned_teachers[1:]:
                assign_committee =assign_teachers_greedy(teacher,committee_students,committee_teachers,y)
                if assign_committee!=-1:
                    supervised_thesis=[i for i in range(N) if t[i]==teacher]
                    assign_thesis_greedy(supervised_thesis,committee_students, x,{assign_committee})
            #Put unrelated thesis and teacher to committees 
            remaining_thesis=[i for i in range(N) if x[i] == -1]  
            assign_thesis_greedy(remaining_thesis,committee_students,x)
            for teacher in range(M):
                if y[teacher]==-1:
                    assign_teachers_greedy(teacher, committee_students, committee_teachers, y)     
        #Ensure minimum requirements
        ensure_minimum_requirements(committee_students, committee_teachers, x, y)
        return x, y
    
    #Local search to improve the solution
    def local_search(x, y,max_iterations=1000):
        current_x,current_y =x[:],y[:]
        #If the initial solution is not feasible, try to fix it
        for attempt in range(10):
            temp_x, temp_y=greedy()
            if is_feasible(temp_x,temp_y):
                current_x, current_y = temp_x, temp_y
                break
        if not is_feasible(current_x,current_y):
            return current_x, current_y  #Best effort
        current_value=calculate_objective(current_x, current_y)
        best_x, best_y=current_x[:], current_y[:]
        best_value=current_value
        
        for iteration in range(max_iterations):
            #Try to move a thesis to another committee
            if random.random() < 0.5:
                thesis=random.randint(0,N-1)
                old_committee=current_x[thesis]
                new_committee=random.randint(0,K-1)
                if old_committee!=new_committee:
                    new_x=current_x[:]
                    new_x[thesis]=new_committee
                    if is_feasible(new_x, current_y):
                        new_value=calculate_objective(new_x,current_y)
                        if new_value>current_value:
                            current_x=new_x
                            current_value=new_value
                            if new_value > best_value:
                                best_x, best_y = new_x[:], current_y[:]
                                best_value=new_value
            #Try to move a teacher to another committee
            else:
                teacher=random.randint(0,M-1)
                old_committee=current_y[teacher]
                new_committee=random.randint(0,K-1)
                if old_committee!=new_committee:
                    new_y=current_y[:]
                    new_y[teacher]=new_committee
                    if is_feasible(current_x, new_y):
                        new_value=calculate_objective(current_x,new_y)
                        if new_value>current_value:
                            current_y=new_y
                            current_value=new_value
                            if new_value > best_value:
                                best_x, best_y = current_x[:], new_y[:]
                                best_value=new_value
        return best_x, best_y
    
    #Try to run multiple time
    best_x,best_y = None, None
    best_score = -1 
    for attempt in range(10):
        try:
            x, y = greedy()
            if is_feasible(x, y):
                x, y = local_search(x, y)
                if is_feasible(x, y):
                    score = calculate_objective(x, y)
                    if score > best_score:
                        best_x, best_y = x, y
                        best_score = score
        except:
            continue
        
    #Return 1-indexed result   
    best_x = [xi + 1 for xi in best_x]
    best_y = [yj + 1 for yj in best_y]
    # Output
    print(N)
    print(' '.join(map(str, best_x)))
    print(M)
    print(' '.join(map(str, best_y)))

# Chạy thuật toán
if __name__ == "__main__":
    solve()
                        
                