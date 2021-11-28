import streamlit as st
import pickle
import altair as alt

import pandas as pd
import numpy as np

def main():
    st.title("CBIR Search Engine")

    text_exp = st.sidebar.expander("Text search")
    with text_exp:
        
        text_search = st.text_input("Search by text", help="Enter a text/keyword for text search")


        search_fields = st.multiselect("Select search fields", options=["Title","Label","Tags"], help='Enter the fields to search in')

        if (search_fields):
            st.markdown('''**Fields boost weights**''')

            for i in range(len(search_fields)):
                st.number_input(search_fields[i],min_value=1,key=i,help="Enter the boost weight")


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
        
        search_res_numbers = st.slider("Number of search results",min_value=1,max_value=50,value=5,help="Select the number of resulted queries")
    


    st.subheader("How to use this app")
    st.markdown(f""" This application is the result of our work on context and text based image retrieval. This app works as google
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

if __name__ == '__main__':
    main()