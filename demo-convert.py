#!/usr/bin/env python

from pathlib import Path
from collections import defaultdict
from collections import OrderedDict
import re
import json
import sys
import os
import unicodedata
import xml.etree.ElementTree as ET 
from shutil import rmtree
import os, fnmatch


class Doc:
    
    # Pendiente documentar todo

    # Obtener curso
    def __makeCourse(self):
        """
        Create a list of chapters by reading course.xml
        """
        course_file_list = list(self.course_path.iterdir())
        self.course_file = [x for x in course_file_list if x.suffix == '.xml'][0]
        course_txt = self.course_file.open().readlines()
        for cline in course_txt:
            if 'chapter' in cline:
                chap_name = cline.split('"')[1]
                self.chapter_list.append(chap_name)
    
    
    def crear_CSS(self):
        
        estilos = open(str(self.path)+'/course-html/css/estilos.css', 'w')
        
        estilos.write('.navegacion ul{\nlist-style: none;\n}\n\n'
          '.menu li a{\ncolor: #353535;\nfont-family: arial;\ntext-decoration: none;\n}\n\n'
          '.menu li a:hover{\ncolor: #CE7D35;\ntransition: all .3s\n}\n\n'
          '.menu>li{\nwidth: auto;\nheight: 20px;\noverflow: hidden;\nfont-weight: 600;\n}\n\n'
          '.menu>li:hover{\ncolor: #CE7D35;\nheight: auto;\ntransition: all .3s;\n}\n\n'
          '.submenu>li{\nfont-weight: 300;}\n\n'
          '.submenu>li>a:hover{\ncolor: #CE7D35;\nmargin-left: 20px;\n}\n\n'
          '.submenu li a{\ndisplay: block;\npadding: 15px;\ncolor" #fff;\ntext-decoration: none;\n}')

        

    def eliminar_carateres_especiales(self, palabra):
        
        trans_tab = dict.fromkeys(map(ord, u'\u0301\u0308'), None)
        palabra = unicodedata.normalize('NFKC', unicodedata.normalize('NFKD', palabra).translate(trans_tab))
        palabra = palabra.replace('?','')
        palabra = palabra.replace('¿','')
        palabra = palabra.replace(':','')
        return palabra

    def limpiar_archivos(self):

        file_path = '%s/static/'%(str(self.path))
        files_to_rename = fnmatch.filter(os.listdir(file_path), '*.*')

        for file_name in files_to_rename:    
            os.rename(file_path + file_name, file_path + file_name.replace('_', '-'))
            os.rename(file_path + file_name, file_path + file_name.replace(' ', '-'))
    
    def obtener_video(self, archivo):

        tree = ET.parse(str(archivo))
        root = tree.getroot()
        url = (root.attrib['youtube_id_1_0'])
        return("https://www.youtube.com/embed/%s" % url)
    
    # Obtener menu principal
    def __makeDraftStruct(self):
        for v in self.draft_vert_path.iterdir():
            if v.suffix != '.xml':
                continue
            v_txt = v.open().readlines()
            fline = v_txt[0]
            sec_name = fline.split('parent_url=')[1].split('"')[1].split('/')[-1].split('@')[-1]
            rank = fline[fline.index('index'):].split('"')[1]
            comp_list = [int(rank), str(v)]
            for vline in v_txt[1:]:
                if '<problem ' in vline:
                    prob = vline.split('"')[1]
                    comp_list.append(['problem',prob])
                elif '<video ' in vline:
                    prob = vline.split('"')[1]
                    comp_list.append(['video', prob])
                elif '<html ' in vline:
                    prob = vline.split('"')[1]
                    comp_list.append(['html', prob])
            if sec_name not in self.draft_problems_struct.keys():
                self.draft_problems_struct[sec_name] = [comp_list]
            else:
                self.draft_problems_struct[sec_name].append(comp_list)
        for k in self.draft_problems_struct:
            sorted_struct = sorted(self.draft_problems_struct[k], key = lambda x: x[0])
            self.draft_problems_struct[k] = [s[1:] for s in sorted_struct]

    # Constructor
    def __init__(self, start_path):
       
        if not os.path.isdir(start_path):
            sys.exit("\033[91m ERROR: can't find directory {} \033[0m".format(start_path))

        ## variables  numericas
        self.first_page = ''
        self.num_seq = 0
        self.num_units = 0
        self.num_pages = 0
        self.num_drafts = 0
        self.tmp_name_equal = ''
        self.type_content = 0

        # Variables de Path
        self.path = Path(start_path)
        self.course_path = self.path / 'course'
        self.chapter_path = self.path / 'chapter'
        self.seq_path = self.path / 'sequential'
        self.vert_path = self.path / 'vertical'

        self.draft_path = self.path / 'drafts'
        self.draft_vert_path = self.draft_path / 'vertical'

        ## Variables auxiliares
        self.aux_course_path = 'course'
        self.aux_chapter_path = 'chapter'
        self.aux_seq_path = 'sequential'
        self.aux_vert_path ='vertical'

        self.aux_draft_path = 'drafts'
        self.aux_draft_vert_path = 'vertical'
        self.file_uno = ''

        ## lista de capitulos
        self.chapter_list = []
        self.pathsHtml = []

        ## Estructura de secciones y unidades
        self.draft_problems_struct = OrderedDict()
        self.public_problems_struct = OrderedDict()
        self.all_problems_struct = OrderedDict()

        self.limpiar_archivos()

        ## obtener estructura del curso
        self.__makeCourse()

        if self.draft_path.exists() and self.draft_vert_path.exists():
            self.__makeDraftStruct()
            


    def describeCourse(self):
        
        if os.path.isdir('%s/course-html'%self.path):
            rmtree('%s/course-html'%self.path)
        os.mkdir('%s/course-html'%self.path)
        os.mkdir('%s/course-html/content'%self.path)
        os.mkdir('%s/course-html/css'%self.path)
        
        readme = open(str(self.path)+'/README.md', 'w')
        index = open(str(self.path)+'/course-html/index.html', 'w') 
        frame_superior = open(str(self.path)+'/course-html/content/frame-superior.html', 'w') 
        frame_izquierdo = open(str(self.path)+'/course-html/content/frame-izquierdo.html', 'w') 
        
        nameCourse = self.course_file.name.replace('.xml','')     
        readme.write("###Course structure - [course/{0}](course/{0})\n".format(self.course_file.name))
        
       
        frame_superior.write('<html>\n<head><title>Frame-Superior</title></head><body bgcolor="white">'
            '<h1>%s\n</h1></body>\n</html>'%nameCourse)

        self.crear_CSS()
        frame_izquierdo.write('<html>\n<head><title>Frame-Derecho</title>\n<link rel="stylesheet" href="../css/estilos.css">'
            '</head><body>\n<nav class="navegacion">\n<ul class="menu">\n<h1>Navegación</h1>\n')

        
        self.describeChapter(readme, frame_izquierdo)
        index.write('<html>\n<head>\n<title>%s</title>\n</head>\n<frameset rows="%s,*" '
            'frameborder="yes" bordercolor="#333" marginwidth="%s" '
            'marginheight="%s"scrolling="no">\n<frame src="content/frame-superior.html" name="superior"></frame>\n'
            '<frameset cols="%s,*" frameborder="yes" bordercolor="#333" marginwidth="%s" marginheight="%s" '
            'scrolling="yes">\n<frame src="content/frame-izquierdo.html" name="izquierdo"</frame>\n'
            '<frame src="content/%s" name="derecho"></frame>\n</frameset>\n</frameset>\n</html'%(nameCourse,
                "18%","10%","10%","20%","10%","30%",self.first_page))

        frame_izquierdo.write('</ul>\n</nav>\n</body>\n</html>')
        readme.close()
        index.close()
        frame_izquierdo.close()


    # Obtener submenu
    def describeChapter(self, readme, frame_izquierdo):
   
        self.crear_CSS()
        for c in self.chapter_list:
            # build path
            c += '.xml'
            cFile = self.chapter_path / c
            aux_cFile = '%s/%s'%(self.aux_chapter_path, c)
            chap_txt = cFile.open().readlines()
            cFile = cFile.relative_to(*cFile.parts[:1])

            first_line = chap_txt[0]
            chap_name = first_line.split('"')[1]

            readme.write('* [Section] {0} - [{1}]({1})\n'.format(chap_name, aux_cFile))

            # Formar menu principal
            frame_izquierdo.write('<li><a href="#">%s</a>'%chap_name)
            
            # Nombre del directorio
            namePath_html = '%s'%(self.eliminar_carateres_especiales(chap_name.replace(' ','-')))
            
            # Crear directorios
            os.mkdir('%s/course-html/content/%s'%(str(self.path),namePath_html))
            
            namePath = self.eliminar_carateres_especiales(chap_name.replace(' ','-'))
            
            self.pathsHtml.append(namePath_html)
            #index.write('<section><h1> %s</h1></section>\n'%(chap_name))

            # eliminar el item inicial
            seq_list = [l.split('"')[1] for l in chap_txt if "sequential" in l]


            pub_seq_struct, all_seq_struct = self.describeSequen(seq_list, readme, frame_izquierdo, namePath)
            frame_izquierdo.write('</li>\n')

            ### estructura publica
            self.public_problems_struct[chap_name] = pub_seq_struct

            self.all_problems_struct['('+c[-9:-4]+')'+chap_name] = (str(cFile), all_seq_struct)
        #print(self.pathsHtml)

        self.public_problems_struct = dict((k, v) for k, v in self.public_problems_struct.items() if v)


    def describeSequen(self, seq, readme, frame_izquierdo, path):

        pub_seq = OrderedDict()
        all_seq = OrderedDict()
        frame_izquierdo.write('\n<ul class="submenu">\n') 
        for s in seq:
            self.num_units = 0;
            count_paths_html = 0;
            unpublished = False
            s_name = s + '.xml'
            sFile = self.seq_path / s_name
            aux_sFile = '%s/%s'%(self.aux_seq_path, s)
            seq_txt = sFile.open().readlines()
            sFile = sFile.relative_to(*sFile.parts[:1])
            first_line = seq_txt[0]
            sequ_name = first_line.split('"')[1]
            readme.write('\t* [Subsection] {0} - [{1}]({1})  \n'.format(sequ_name, aux_sFile))
            self.tmp_name_equal = sequ_name
            if os.path.isdir('%s/course-html/content/%s/%s'%(str(self.path), path,self.eliminar_carateres_especiales(sequ_name).replace(' ','-').lower())):
                self.num_seq =+ 1
                sequ_name = '%s-%d'%(sequ_name,self.num_seq)
            os.mkdir('%s/course-html/content/%s/%s'%(str(self.path), path,self.eliminar_carateres_especiales(sequ_name).replace(' ','-').lower()))
            # Dentro del href colocar las direcciones
            #index.write('')
            #print('%d\n%s\n\n'%(len(seq_txt),seq_txt))
            if len(seq_txt) > 2:
                unit_list = [l.split('"')[1] for l in seq_txt if "vertical" in l]
                if (len(unit_list) > 1):
                    frame_izquierdo.write('<li><a href="#">%s</a></li>\n'%(self.tmp_name_equal))
                    frame_izquierdo.write('<ul class="submenu2">\n') 
                    pub_dict, all_dict = self.describeUnit(unit_list, readme, frame_izquierdo, sequ_name, path)
                    frame_izquierdo.write('</ul>\n')
                else:
                    pub_dict, all_dict = self.describeUnit(unit_list, readme, frame_izquierdo, sequ_name, path)
                pub_seq[sequ_name] = pub_dict

                if s in self.draft_problems_struct.keys():

                    old_list = self.draft_problems_struct[s][:]
                    for u in old_list:
                        u_id = u[0].split('/')[-1].split('.xml')[0]
                        if u_id in unit_list:
                            unpublished = True
                            self.draft_problems_struct[s].remove(u)
                    if self.draft_problems_struct[s]:
                        all_dict2 = self.describeDraftUnit(self.draft_problems_struct[s], readme, frame_izquierdo,sequ_name, path)
                        for d in all_dict2:
                            all_dict[d] = all_dict2[d]

                all_seq['('+s_name[-9:-4]+')'+sequ_name] = (str(sFile), all_dict)

                if unpublished:
                    print('\033[93m Warning: There are unpublished changes in published problems under subsection {}. Only looking at published version.\033[0m'.format(sequ_name))

            else: #check draft
                if s not in self.draft_problems_struct.keys():
                    all_dict = OrderedDict()
                else:
                    all_dict = self.describeDraftUnit(self.draft_problems_struct[s], readme, frame_izquierdo, sequ_name, path)
                all_seq['('+s_name[-9:-4]+')'+sequ_name] = (str(sFile), all_dict)

        frame_izquierdo.write('</ul>\n')
        pub_seq = dict((k, v) for k, v in pub_seq.items() if v)
        return pub_seq, all_seq

    def describeUnit(self, uni, readme, frame_izquierdo,sequ_name, path):
        aux_sequ_name = self.eliminar_carateres_especiales(sequ_name).replace(' ','-')
        #print(uni)
        #print('\n\n')
        pub_uni = OrderedDict()
        all_uni = OrderedDict()

        for u in uni:
            u += '.xml'
            uFile = self.vert_path / u
            aux_uFile = '%s/%s'%(self.aux_vert_path, u)
            uni_txt = uFile.open().readlines()
            uFile = uFile.relative_to(*uFile.parts[:1])
            first_line = uni_txt[0]
            u_name = first_line.split('"')[1]
            readme.write('\t\t* [Unit] {0} - [{1}]({1})\n'.format(u_name, aux_uFile))
            aux_u_name = self.eliminar_carateres_especiales(u_name.replace(' ','-'))
            #print(uni_txt[0])
            
            # Formar el submenu
            if (len(uni) > 1):
                if os.path.isdir('%s/course-html/content/%s/%s'%(str(self.path), path,u_name)):
                    self.num_units+=1
                    aux_u_name = '%s-%d'%(aux_u_name,self.num_units)
                    os.mkdir('%s/course-html/content/%s/%s/%s'%(str(self.path), path, self.eliminar_carateres_especiales(sequ_name).replace(' ','-').lower()
                        ,aux_u_name.lower()))
                else:
                    os.mkdir('%s/course-html/content/%s/%s/%s'%(str(self.path), path, self.eliminar_carateres_especiales(sequ_name).replace(' ','-').lower()
                        , aux_u_name.lower()))
                frame_izquierdo.write('<li><a href="%s/%s/%s/%s.html" target="derecho">%s</a></li>\n'%(path,aux_sequ_name.lower(),aux_u_name.lower(),aux_u_name.lower(),u_name))
                frame_derecho = open(str(self.path)+'/course-html/content/%s/%s/%s/%s.html'%(path,aux_sequ_name.lower(),aux_u_name.lower(),aux_u_name.lower()), 'w')
                self.type_content = 1
            else:
                frame_izquierdo.write('<li><a href="%s/%s/%s.html" target="derecho">%s</a></li>\n'%(path,aux_sequ_name.lower(),aux_u_name.lower(),sequ_name))
                if(self.num_pages == 0):
                    self.first_page = '%s%s/%s/%s.html'%(self.first_page,path,aux_sequ_name.lower(),aux_u_name.lower())
                    self.num_pages+=1
                 # Crear los archivos.html en el directorio creado para cada section
                frame_derecho = open(str(self.path)+'/course-html/content/%s/%s/%s.html'%(path,aux_sequ_name.lower(),aux_u_name.lower()), 'w')
                self.type_content = 0
           
            
            prob_list = []
            for l in uni_txt[1:]:
                if '<problem ' in l:
                    prob = l.split('"')[1]
                    prob_list.append(['problem',prob])
                elif '<video ' in l:
                    prob = l.split('"')[1]
                    prob_list.append(['video', prob])
                elif '<html ' in l:
                    prob = l.split('"')[1]
                    prob_list.append(['html', prob])
                #elif '<discussion ' in l:
                #    prob = l.split('"')[1]
                #    comp_list.append(['discussion', prob])

            #print(prob_list)

            pub_dict, all_dict = self.describeProb(prob_list, readme, frame_derecho)
            frame_derecho.close()
            pub_uni[u_name] = pub_dict
            all_uni['('+u[-9:-4]+')'+u_name] = (str(uFile), all_dict)
        pub_uni = dict((k, v) for k, v in pub_uni.items() if v)
        return pub_uni, all_uni

    def describeProb(self, prob_list, readme, frame_derecho):
        
        '''
        print(prob_list)
        print(len(prob_list))
        print('\n\n')
        '''
        """
        Write component information into readme
        Input:
            [prob_list]: the list of problems to describe further
        """
        pub_prob = OrderedDict()
        pro_list = []

        pat1 = re.compile(r'<problem ([^>]+)>')
        pat2 = re.compile(r'(\S+)="([^"]+)"')

        for pro in prob_list:
            # Pendiente agregar condicion para ver si es un video o un html.
            if pro[0] == 'html': # Condicion para ver si el archivo es un html
                pro_name = pro[1]+'.xml'
                pro_name_html = pro[1]+'.html' # obtener el arhivo html
                
                pFile = self.path / pro[0] / pro_name
                pFile_html = self.path / pro[0] / pro_name_html
                
                aux_pFile = '%s/%s'%(pro[0], pro_name)
                
                p_txt = pFile.open().readlines()
                p_txt_html = pFile_html.open().readlines()
                pFile = pFile.relative_to(*pFile.parts[:1])
                fline = p_txt[0]
                m = pat1.match(fline)
                #print(m)
                if m:
                    params = m.group(1)
                    m2 = pat2.findall(params)
                    Dict= {key:val for key,val in m2 if key!='markdown'}
                    p_name = Dict['display_name']
                    if 'weight' in Dict.keys():
                        weight = Dict['weight']
                        if 'max_attempts' in Dict.keys():
                            max_att = Dict['max_attempts']
                            pub_prob[p_name] = {'file':pro_name, 'weight':Dict['weight'], 'max_attempts':Dict['max_attempts']}
                        else:
                            pub_prob[p_name] = {'file':pro_name, 'weight':Dict['weight']}
                    #print('\t\t\t* [{0}] {1} - [{2}]({2})\n'.format(pro[0], p_name, aux_pFile))
                    readme.write('\t\t\t* [{0}] {1} - [{2}]({2})\n'.format(pro[0], p_name, aux_pFile))
                    #readme.write('\t\t\t\t Weight: {0}, Max Attempts: {1}\n'.format(weight, max_att))
                else:
                    readme.write('\t\t\t* [{0}] - [{1}]({1})\n'.format(pro[0], aux_pFile))
                    #print(str(p_txt_html))
                    for text in p_txt_html:
                        for line in text.split('\n'):
                            line = line.replace('_','-')
                            if self.type_content == 0:
                                frame_derecho.write('%s\n'%line.replace('/static/','../../../../static/'))
                            else:
                                frame_derecho.write('%s\n'%line.replace('/static/','../../../../../static/'))
                
                pro_list.append((str(pFile), pro[0]))
            elif pro[0] == 'video':
                pro_name = pro[1]+'.xml'
                pFile = self.path / pro[0] / pro_name
                frame_derecho.write('<iframe class=»youtube-player» type=»text/html» width=»846″ height=»484″ src=%s ' 
                    'frameborder=»0″></iframe>\n'%self.obtener_video(pFile))

                
        return pub_prob, pro_list

    # Obtener informacion de unidades
    def describeDraftUnit(self, unit, readme, frame_izquierdo,sequ_name, path):
        aux_sequ_name = self.eliminar_carateres_especiales(sequ_name).replace(' ','-')
        all_uni = OrderedDict()
        for u in unit:
            uFile = Path(u[0])
            aux_uFile = u[0].split('/')
            aux_uFile = '%s/%s/%s'%(aux_uFile[-3],aux_uFile[-2],aux_uFile[-1])
            first_line = uFile.open().readlines()[0]
            uFile = uFile.relative_to(*uFile.parts[:1])
            u_name = first_line.split('"')[1]
            aux_u_name = self.eliminar_carateres_especiales(u_name.replace(' ','-'))
            
            if os.path.isdir('%s/course-html/content/%s/%s/%s'%(str(self.path), path, self.eliminar_carateres_especiales(sequ_name).replace(' ','-').lower()
                ,aux_u_name.lower())):
                self.num_drafts+=1
                aux_u_name = '%s-%d'%(aux_u_name,self.num_drafts)
            
            os.mkdir('%s/course-html/content/%s/%s/%s'%(str(self.path), path, self.eliminar_carateres_especiales(sequ_name).replace(' ','-').lower()
                , aux_u_name.lower()))
            
            frame_izquierdo.write('<li><a href="%s/%s/%s/%s.html" target="derecho">%s</a></li>\n'%(path,aux_sequ_name.lower(),
                aux_u_name.lower(),aux_u_name.lower(),u_name))

            frame_derecho = open(str(self.path)+'/course-html/content/%s/%s/%s/%s.html'%(path,aux_sequ_name.lower(),aux_u_name.lower(),aux_u_name.lower()), 'w')

            readme.write('\t\t* [Unit]\(Draft\) {0} - [{1}]({1})\n'.format(u_name, aux_uFile))
            prob_list = self.describeDraftProb(u[1:], readme,frame_derecho)
            frame_derecho.close()
            all_uni['('+u[0][-9:-4]+')(draft)'+u_name] = (str(uFile), prob_list)
        return all_uni

    
    def describeDraftProb(self, probs, readme,frame_derecho):
  
        prob_list = []
        for pro in probs:
            pro_name = pro[1]+'.xml'
            pro_name_html = pro[1]+'.html'
            pFile = self.draft_path / pro[0] / pro_name
            aux_pFile = '%s/%s/%s'%(self.aux_draft_path,pro[0],pro_name_html)
            
            pFile_html = self.draft_path / pro[0] / pro_name_html
            
            p_txt = pFile.open().readlines()

            p_txt_html = pFile_html.open().readlines()
    
            pFile = pFile.relative_to(*pFile.parts[:1])
            fline = p_txt[0]
            p_name = fline.split('"')[1]
            if pro[0] == 'problem':
                readme.write('\t\t\t* [{0}]\(Draft\) {1} - [{2}]({2})\n'.format(pro[0], p_name, aux_pFile))
            else:
                readme.write('\t\t\t* [{0}]\(Draft\) - [{1}]({1})\n'.format(pro[0], aux_pFile))
                for text in p_txt_html:
                        for line in text.split('\n'):
                            frame_derecho.write('%s\n'%line.replace('/static/','../../../../static/'))
            prob_list.append((str(pFile), '(draft)'+pro[0]))
        return prob_list


if __name__ == "__main__":

    if len(sys.argv) != 2:
        pass
    else:
        folder_name = sys.argv[1]
        os.getcwd()
    # Aqui cambiar por la ruta donde tienen alojado el curso descargado.
    #writeDoc = Doc('/home/carloscastillo/Escritorio/course')
    writeDoc = Doc(os.getcwd())
    writeDoc.describeCourse()
    #all_prob_dict = writeDoc.all_problems_struct


