from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import plotly.express as px
import plotly.graph_objects as go
import json
import plotly

def analyze_data():
    try:
        # Đọc dữ liệu từ file CSV
        df_videos = pd.read_csv('data/videos.csv')
        df_trending = pd.read_csv('data/trending_videos.csv')
        
        # Phân tích cơ bản
        analysis = {
            'total_videos': len(df_videos),
            'total_trending': len(df_trending),
            'trending_rate': (len(df_trending) / len(df_videos)) * 100,
            
            # Phân tích theo thể loại
            'category_analysis': df_trending['category'].value_counts().to_dict(),
            
            # Thống kê cơ bản
            'avg_views': df_trending['views'].mean(),
            'avg_likes': df_trending['likes'].mean(),
            'avg_comments': df_trending['comments'].mean(),
            
            # Tương quan giữa các chỉ số
            'correlations': {
                'views_likes': df_trending['views'].corr(df_trending['likes']),
                'views_comments': df_trending['views'].corr(df_trending['comments']),
                'likes_comments': df_trending['likes'].corr(df_trending['comments'])
            }
        }
        
        # Tạo biểu đồ tương quan
        plt.figure(figsize=(10, 6))
        sns.heatmap(df_trending[['views', 'likes', 'comments', 'dislikes']].corr(), 
                   annot=True, cmap='coolwarm')
        plt.title('Tương quan giữa các chỉ số của video trending')
        
        # Lưu biểu đồ vào buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        # Chuyển đổi biểu đồ thành base64 để hiển thị trên web
        analysis['correlation_plot'] = base64.b64encode(image_png).decode('utf-8')
        
        return analysis
    except Exception as e:
        print(f"Lỗi khi phân tích dữ liệu: {str(e)}")
        return None

def index(request):
    try:
        # Đọc dữ liệu từ file CSV
        trending_df = pd.read_csv('data/youtube_trending_vn.csv')
        analysis_df = pd.read_csv('data/youtube_videos_analysis.csv')
        
        # Tính toán thống kê tổng quan
        total_videos = len(analysis_df)
        total_trending = len(trending_df)
        trending_rate = (total_trending / total_videos) * 100
        avg_views = trending_df['view_count'].mean()
        
        # Tạo biểu đồ tương quan giữa lượt xem và lượt thích
        fig1 = px.scatter(trending_df, 
                         x='view_count', 
                         y='like_count',
                         title='Tương quan giữa lượt xem và lượt thích của video trending',
                         labels={'view_count': 'Lượt xem', 'like_count': 'Lượt thích'},
                         color='category_id',
                         hover_data=['title', 'channel_title'])
        
        # Tạo biểu đồ phân bố thời lượng video
        fig2 = px.histogram(trending_df,
                           x='duration',
                           title='Phân bố thời lượng video trending',
                           labels={'duration': 'Thời lượng', 'count': 'Số lượng video'},
                           nbins=50)
        
        # Tạo biểu đồ top 10 kênh có nhiều video trending nhất
        top_channels = trending_df['channel_title'].value_counts().head(10)
        fig3 = px.bar(x=top_channels.index, 
                     y=top_channels.values,
                     title='Top 10 kênh có nhiều video trending nhất',
                     labels={'x': 'Tên kênh', 'y': 'Số video trending'})
        
        # Tạo biểu đồ tương quan giữa số người đăng ký và lượt xem
        fig4 = px.scatter(trending_df,
                         x='channel_subscribers',
                         y='view_count',
                         title='Tương quan giữa số người đăng ký và lượt xem',
                         labels={'channel_subscribers': 'Số người đăng ký', 'view_count': 'Lượt xem'},
                         color='category_id',
                         hover_data=['title', 'channel_title'])
        
        # Tạo biểu đồ phân bố theo thể loại
        category_counts = trending_df['category_id'].value_counts()
        fig5 = px.pie(values=category_counts.values,
                     names=category_counts.index,
                     title='Phân bố video trending theo thể loại')
        
        # Cập nhật layout cho các biểu đồ
        for fig in [fig1, fig2, fig3, fig4, fig5]:
            fig.update_layout(
                template='plotly_white',
                font=dict(family="Arial", size=12),
                margin=dict(l=50, r=50, t=50, b=50),
                showlegend=True,
                height=400
            )
        
        # Chuyển các biểu đồ thành JSON string
        graphs = {
            'view_like_correlation': json.loads(json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)),
            'duration_distribution': json.loads(json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)),
            'top_channels': json.loads(json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)),
            'subscriber_view_correlation': json.loads(json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)),
            'category_distribution': json.loads(json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder))
        }
        graphs_json = json.dumps(graphs)
        
        context = {
            'total_videos': total_videos,
            'total_trending': total_trending,
            'trending_rate': trending_rate,
            'avg_views': avg_views,
            'graphs': graphs_json
        }
        
        return render(request, "index.html", context)
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return render(request, "index.html", {
            'error': f"Có lỗi xảy ra: {str(e)}"
        })

def analyze_trending_videos(request):
    # Đọc dữ liệu từ file CSV
    trending_df = pd.read_csv('data/youtube_trending_vn.csv')
    analysis_df = pd.read_csv('data/youtube_videos_analysis.csv')
    
    # Tính toán thống kê tổng quan
    total_videos = len(analysis_df)
    total_trending = len(trending_df)
    trending_rate = (total_trending / total_videos) * 100
    avg_views = trending_df['view_count'].mean()
    
    # Tạo biểu đồ tương quan giữa lượt xem và lượt thích
    fig1 = px.scatter(trending_df, 
                     x='view_count', 
                     y='like_count',
                     title='Tương quan giữa lượt xem và lượt thích của video trending',
                     labels={'view_count': 'Lượt xem', 'like_count': 'Lượt thích'},
                     color='category_id',
                     hover_data=['title', 'channel_title'])
    
    # Tạo biểu đồ phân bố thời lượng video
    fig2 = px.histogram(trending_df,
                       x='duration',
                       title='Phân bố thời lượng video trending',
                       labels={'duration': 'Thời lượng', 'count': 'Số lượng video'},
                       nbins=50)
    
    # Tạo biểu đồ top 10 kênh có nhiều video trending nhất
    top_channels = trending_df['channel_title'].value_counts().head(10)
    fig3 = px.bar(x=top_channels.index, 
                 y=top_channels.values,
                 title='Top 10 kênh có nhiều video trending nhất',
                 labels={'x': 'Tên kênh', 'y': 'Số video trending'})
    
    # Tạo biểu đồ tương quan giữa số người đăng ký và lượt xem
    fig4 = px.scatter(trending_df,
                     x='channel_subscribers',
                     y='view_count',
                     title='Tương quan giữa số người đăng ký và lượt xem',
                     labels={'channel_subscribers': 'Số người đăng ký', 'view_count': 'Lượt xem'},
                     color='category_id',
                     hover_data=['title', 'channel_title'])
    
    # Tạo biểu đồ phân bố theo thể loại
    category_counts = trending_df['category_id'].value_counts()
    fig5 = px.pie(values=category_counts.values,
                 names=category_counts.index,
                 title='Phân bố video trending theo thể loại')
    
    # Cập nhật layout cho các biểu đồ
    for fig in [fig1, fig2, fig3, fig4, fig5]:
        fig.update_layout(
            template='plotly_white',
            font=dict(family="Arial", size=12),
            margin=dict(l=50, r=50, t=50, b=50),
            showlegend=True
        )
    
    # Chuyển các biểu đồ thành JSON
    graphs = {
        'view_like_correlation': json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder),
        'duration_distribution': json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder),
        'top_channels': json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder),
        'subscriber_view_correlation': json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder),
        'category_distribution': json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)
    }
    
    context = {
        'total_videos': total_videos,
        'total_trending': total_trending,
        'trending_rate': trending_rate,
        'avg_views': avg_views,
        'graphs': graphs
    }
    
    return render(request, 'predictor/analysis.html', context)