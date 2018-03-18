# Gitea client


```python
cl = j.clients.gitea.get()



names=[item for item in cl.orgs_currentuser_list().keys()]
names.sort()

for name in names:
    org = cl.org_get(name)

    #CAREFULL WILL GO OVER ALL MILESTONES & LABELS and add them
    org.labels_milestones_add(remove_old=False)


    repoName=[item for item in org.repos_list().keys()][0] #first reponame

    repo = org.repo_get(repoName)

    # repo.labels_add()
    # repo.milestones_add(remove_old=False)


```