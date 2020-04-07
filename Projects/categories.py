from stats_can import * 

if __name__ == "__main__":

    
    
    

    


    cols = list(df_fullDATA.loc[:,'REF_DATE':'UOM'])+ ['SCALAR_FACTOR'] +  ['VALUE']
    df_less = df_fullDATA[cols]
    df_less2 = df_less.drop(["DGUID"], axis=1)
    df_less2 = df_less2.replace({"Aboriginal": "Indigenous"},regex=True)

    df_less2  = df_less2.rename(columns={"Aboriginal group": "Indigenous group"})
    df_less2.head()

    iteration_nr = df_less2.shape[1]
    categories = []
    for i in range(iteration_nr-1):
        categories.append(df_less2.iloc[:,i].unique())


    all_the_widgets = []
    for i in range(len(categories)):
        if i==0:
            a_category = widgets.Dropdown(
                    value = categories[i][0],
                    options = categories[i], 
                    description ='Start Date:', 
                    style = style, 
                    disabled=False
                )
            b_category = widgets.Dropdown(
                    value = categories[i][-1],
                    options = categories[i], 
                    description ='End Date:', 
                    style = style, 
                    disabled=False
                )
            all_the_widgets.append(a_category)
            all_the_widgets.append(b_category)
        elif i==1:
            a_category = widgets.Dropdown(
                    value = categories[i][0],
                    options = categories[i], 
                    description ='Location:', 
                    style = style, 
                    disabled=False
                )
            all_the_widgets.append(a_category)
        elif i==len(categories)-1:
            a_category = widgets.Dropdown(
                    value = categories[i][0],
                    options = categories[i], 
                    description ='Scalar factor:', 
                    style = style, 
                    disabled=False
                )
            all_the_widgets.append(a_category)

        elif i==len(categories)-2:
            a_category = widgets.Dropdown(
                    value = categories[i][0],
                    options = categories[i], 
                    description ='Units of Measure :', 
                    style = style, 
                    disabled=False
                )
            all_the_widgets.append(a_category)
        else:
            a_category = widgets.Dropdown(
                    value = categories[i][0],
                    options = categories[i], 
                    description ='Subcategory ' + str(i), 
                    style = style, 
                    disabled=False
                )
            all_the_widgets.append(a_category)
