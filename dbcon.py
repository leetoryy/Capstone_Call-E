import pymysql

child_conn = None
child_cur = None

child_conn = pymysql.connect(host='orion.mokpo.ac.kr',
                       port=8397,
                       user='root',
                       passwd='ScE1234**',
                       db='CHILD', 
                       charset='utf8')
child_cur = child_conn.cursor()

#=====

calle_conn = None
calle_cur = None

calle_conn = pymysql.connect(host='orion.mokpo.ac.kr',
                       port=8397,
                       user='root',
                       passwd='ScE1234**',
                       db='CALL_E', 
                       charset='utf8')
calle_cur = calle_conn.cursor()

#=====
counselor_conn = None
counselor_cur = None

counselor_conn = pymysql.connect(host='orion.mokpo.ac.kr',
                       port=8397,
                       user='root',
                       passwd='ScE1234**',
                       db='COUNSELOR', 
                       charset='utf8')
counselor_cur = counselor_conn.cursor()

#=====
child_info_conn = None
child_info_cur = None

child_info_conn = pymysql.connect(host='orion.mokpo.ac.kr',
                       port=8397,
                       user='root',
                       passwd='ScE1234**',
                       db='CHILD_INFO', 
                       charset='utf8')
child_info_cur = child_info_conn.cursor()

#=====
review_list_conn = None
review_list_cur = None

review_list_conn = pymysql.connect(host='orion.mokpo.ac.kr',
                       port=8397,
                       user='root',
                       passwd='ScE1234**',
                       db='REVIEW', 
                       charset='utf8')
review_list_cur = review_list_conn.cursor()