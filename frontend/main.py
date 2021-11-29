import requests
import templates
import validators
import streamlit as st


def set_session_state():
    # default values
    if 'recursive' not in st.session_state:
        st.session_state.recursive = None
    if 'search_term' not in st.session_state:
        st.session_state.search_term = None
    
    # get parameters in url
    para = st.experimental_get_query_params()

    if 'recursive' in para:
        st.experimental_set_query_params()
        st.session_state.recursive = para['recursive'][0]
    if 'search-term' in para:
        st.experimental_set_query_params()
        st.session_state.search_term = para['search-term'][0]

def tutorial():
    st.subheader("How to use this app")
    st.write(f"""
        This application is the result of our work on context and text based image retrieval. This app works as google
            search do. 
            \n You can search similar images by using a word or sentance, by provinding an another image, by provinding another image
            by directly using its link and finally you can search similar images using a query image and text query (Ex. Dog image + Black as the text query = Black dogs).
            \n In addition, you can do recusive search by clicking on an image from the results.
    #### Filters
    you can refine your query based on the fields to search on, whether to use fuzzy searching and how many result per query.
    - **Fuzzy search**: Returns documents that contain terms similar to the search term
    - **Image & Text**: Use both image and text query
    - **Number of search results**: Specify the number of images to be returned when you search.
        """)
            
    st.subheader("About")
    st.markdown(
                    f""" We are [Ghazi Tounsi](https://github.com/GhaziXX) and [Mohamed Karaa](https://github.com/mohamedkaraa) a final year ICT engineering students
                    at the Higher School of Communication of Tunis (Sup'Com). We have an keen intrest on deep learning specifically computer vision and software engineering.  
                    \n This work is part of our study where we combine computer vision, elasticsearch and Approximate Neural Networks to create an image similarity search engine.
                    """)

    st.subheader("Appendix: Data & methods")
    st.markdown(f""" We have used the [open images dataset](https://github.com/cvdfoundation/open-images-dataset#download-full-dataset-with-google-storage-transfer) provided by google and extracted about 2.2M images from it.
                    \n We have used the [Flickr API](https://www.flickr.com/services/api/) (as the data is all from flickr) to get the images tags and titles and used the Lables from the dataset.
                    \n We then used VGG16 for feature extraction and PCA for Dimentionality reduction along to [ElasticSearch](https://www.elastic.co/) and [Elastiknn](https://elastiknn.com/) for indexing the images.
                    \n If you want to reproduce the result you can visit the github [repo](https://github.com/GhaziXX/context-and-text-based-image-retrieval)
                    """)

def init_view():
    if st.session_state.search_term is None:
        text_exp = st.sidebar.expander("Text search", False)
    else:
        text_exp = st.sidebar.expander("Text search", True)
    
    with text_exp:
        if st.session_state.search_term is None:
            text_search = st.text_input("Search by text", help="Enter a text/keyword for text search")
        else:
            text_search = st.text_input("Search by text",st.session_state.search_term, help="Enter a text/keyword for text search")
        
        search_fields = st.multiselect("Select search fields", options=["Title","Labels","Tags"], help='Enter the fields to search in')
        
        number_inputs = {}
        
        if (search_fields):
            st.markdown('''**Fields boost weights**''')

            for i in range(len(search_fields)):
                number_inputs[str(i)] = st.number_input(search_fields[i],min_value=1,key=i,help="Enter the boost weight")
            

    img_exp = st.sidebar.expander("Image search")
    with img_exp:
        link_search = st.text_input("Search by image link", help="Enter an image link here for image search")

        img_search = st.file_uploader("Upload an image",type = ["jpg","png"],help="Drag and drop your image here")

    filter_exp = st.sidebar.expander("Filters")
    with filter_exp:
        layout = st.columns([1, 1])

        with layout[0]: 
            use_fuzzy = st.checkbox('Fuzzy search',help="Use fuzzy (non excat search)") # omit "sidebar"
    
        with layout[-1]: 
            use_text_image = st.checkbox('Image & Text',help="Use a combined image and text query") 
        
        start_from = st.number_input("Index to start from: ",min_value=0,value=0,step=1)
        search_res_numbers = st.slider("Number of search results",min_value=1,max_value=50,value=5,help="Select the number of resulted queries")
        
        
    
    _, _, col3 , _, _ = st.sidebar.columns(5)
    
    with col3 :
        search = st.button("Search", help="click here to search")
    
        
    return text_search, search_fields, number_inputs, link_search, img_search, use_fuzzy, use_text_image, search_res_numbers, search, start_from

def text_search_query(search_res_numbers, text_search, use_fuzzy, fields,from_):
    
    fields = '{"labels":5, "tags":1, "title":2}' if fields == {} else fields
    
    headers = {'accept': 'application/json'}
    params = (('query', text_search),('fields', fields),('use_fuzzy', use_fuzzy),('size', str(search_res_numbers)),('from_', str(from_)),)
    
    try:
        response = requests.get(f"http://localhost:8080/api/v1/text_query", headers=headers, params=params)
        results = response.json()
        total_hits = results['hits']['total']['value']
    except Exception as e:
        total_hits = 0
        
    if total_hits > 0:
        
        st.write(templates.number_of_results(total_hits, results['took'] / 1000),
                unsafe_allow_html=True)
        
        for i in range(len(results['hits']['hits'])):
            result = results['hits']['hits'][i]
            res = {}
            res["url"] = result['_source']["imgUrl"]
            res['title'] = result['_source']["title"]
            res['labels'] = result['_source']["labels"]
            res['score'] = result["_score"]
            res["id"] = result['_source']["imageId"]
            res["search_term"] = text_search
            st.write(templates.search_result(i, **res), unsafe_allow_html=True)
            st.write(templates.tag_boxes(result['_source']['tags']),
                    unsafe_allow_html=True)
            
    else:
        st.write(templates.no_result_html(), unsafe_allow_html=True)   

def recursive_search(search_res_numbers, text_search, from_):
    
    headers = {'accept': 'application/json'}
    params = (('image_id', st.session_state.recursive),('size', str(search_res_numbers)),('from_', str(from_)),('condidates', '100'),)
    
    try:
        response = requests.post(f"http://localhost:8080/api/v1/image_query", headers=headers, params=params)
        results = response.json()
        total_hits = results['hits']['total']['value']
    except:
        total_hits = 0
    
    if total_hits > 0:
        st.write(templates.number_of_results(total_hits, results['took'] / 1000),
                unsafe_allow_html=True)
        
        # search results
        for i in range(len(results['hits']['hits'])):
            result = results['hits']['hits'][i]
            res = {}
            res["url"] = result['_source']["imgUrl"]
            res['title'] = result['_source']["title"]
            res['labels'] = result['_source']["labels"]
            res['score'] = result["_score"]
            res["id"] = result['_source']["imageId"]
            res["search_term"] = text_search
            st.write(templates.search_result(i, **res), unsafe_allow_html=True)
            st.write(templates.tag_boxes(result['_source']['tags']),
                    unsafe_allow_html=True)
    else:
        st.write(templates.no_result_html(), unsafe_allow_html=True)

def image_search_query(search_res_numbers, use_fuzzy, fields, from_ = None, link_search=None, img_search=None, text_search=None, use_text_image=False):
        
    fields = '{"labels":5, "tags":1, "title":2}' if fields == {} or fields == '}' else fields
    
    headers = {'accept': 'application/json'}
    
    if link_search and img_search == None:
        if validators.url(link_search):
            if use_text_image:
                params = (('image_link', link_search),('size', str(search_res_numbers)),
                ('from_', str(from_)),('condidates', '100'),('query',text_search),('fields',fields), 
                ('use_fuzzy',use_fuzzy),)
                show_results(headers=headers, params=params, text_search=text_search, call_type = 'image-text')
                
            else:
                params = (('image_link', link_search),('size', str(search_res_numbers)),
                ('from_', str(from_)),('condidates', '100'),)
                show_results(headers=headers, params=params, text_search=text_search, call_type = 'image')
                
    elif img_search and not link_search:
        headers = {'accept': 'application/json'}
        files = {'image': img_search.getvalue(),}
        
        if use_text_image:
            params = (('size', str(search_res_numbers)),('from_', str(from_)),
                     ('condidates', '100'),('query',text_search),('fields',fields), ('use_fuzzy',use_fuzzy),)
            show_results(headers=headers, params=params, files=files, text_search=text_search, call_type = 'image-text')
           
        else:
            params = (('size', str(search_res_numbers)),('from_', str(from_)),('condidates', '100'),)
            
            show_results(headers=headers, params=params, files=files, text_search=text_search, call_type = 'image')
    else:
        st.write(templates.one_type_html(), unsafe_allow_html=True)

def show_results(headers, params ,text_search, call_type = None, files=None):
    try:
        if call_type == "image":
            if files:
                response = requests.post(f"http://localhost:8080/api/v1/image_query", headers=headers, params=params, files=files)
            else:
                response = requests.post(f"http://localhost:8080/api/v1/image_query", headers=headers, params=params)
        elif call_type == "image-text":
            if files:
                response = requests.post(f"http://localhost:8080/api/v1/text_image_query", headers=headers, params=params, files=files)
            else:
                response = requests.post(f"http://localhost:8080/api/v1/text_image_query", headers=headers, params=params)
            
        results = response.json()
        total_hits = results['hits']['total']['value']
    except Exception as e:
        total_hits = 0
        
    if total_hits > 0:
        st.write(templates.number_of_results(total_hits, results['took'] / 1000),
                unsafe_allow_html=True)
        
        for i in range(len(results['hits']['hits'])):
            result = results['hits']['hits'][i]
            res = {}
            res["url"] = result['_source']["imgUrl"]
            res['title'] = result['_source']["title"]
            res['labels'] = result['_source']["labels"]
            res['score'] = result["_score"]
            res["id"] = result['_source']["imageId"]
            res["search_term"] = text_search
            st.write(templates.search_result(i, **res), unsafe_allow_html=True)
            st.write(templates.tag_boxes(result['_source']['tags']),
                    unsafe_allow_html=True)
    else:
        st.write(templates.no_result_html(), unsafe_allow_html=True)
        
def main():
    st.set_page_config(page_title='CBIR Search Engine')
    
    set_session_state()
    
    st.title("CBIR Search Engine")
    st.write(templates.load_css(), unsafe_allow_html=True)
    
    text_search, search_fields, number_inputs, link_search, img_search, use_fuzzy, use_text_image, search_res_numbers, search, from_ = init_view()
    
    fields = {search_fields[i].lower():number_inputs[str(i)] for i in range(len(search_fields))}
    fields_str = '{'
    for elem in fields.items():
        fields_str+=f'"{elem[0]}":{elem[1]},'
    fields_str = fields_str[:-1]+'}'
    if search:
        if img_search or link_search:
            image_search_query(search_res_numbers=search_res_numbers,
                               use_fuzzy=use_fuzzy,
                               fields=fields_str,
                               from_=int(from_),
                               link_search=link_search,
                               img_search=img_search,
                               text_search=text_search,
                               use_text_image=use_text_image
                               )
        else:
            text_search_query(search_res_numbers=search_res_numbers, text_search=text_search, use_fuzzy=use_fuzzy, fields=fields_str, from_=int(from_))
        st.session_state.recursive = None
        
    elif st.session_state.recursive != None:
        recursive_search(search_res_numbers=search_res_numbers, text_search=text_search, from_=int(from_))
    
    else:
        tutorial()

if __name__ == '__main__':
    main()
    