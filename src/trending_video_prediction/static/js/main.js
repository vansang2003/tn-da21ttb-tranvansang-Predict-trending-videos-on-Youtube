// Biến toàn cục
let videos = [];
let currentPage = 1;
const itemsPerPage = 12;

// Hàm format số
function formatNumber(num) {
    return new Intl.NumberFormat('vi-VN').format(num);
}

// Hàm format thời gian
function formatDuration(duration) {
    if (!duration) return 'N/A';
    const match = duration.match(/PT(\d+H)?(\d+M)?(\d+S)?/);
    if (!match) return duration;
    
    const hours = (match[1] || '').replace('H', '');
    const minutes = (match[2] || '').replace('M', '');
    const seconds = (match[3] || '').replace('S', '');
    
    let result = '';
    if (hours) result += hours + ':';
    result += (minutes || '0').padStart(2, '0') + ':';
    result += (seconds || '0').padStart(2, '0');
    
    return result;
}

// Hàm tạo card video
function createVideoCard(video) {
    return `
        <div class="col-md-4">
            <div class="card video-card">
                <img src="${video.thumbnail_url || video.thumbnail_high}" class="card-img-top" alt="${video.title}">
                <div class="card-body">
                    <h5 class="card-title">${video.title}</h5>
                    <p class="card-text">
                        <small class="text-muted">Kênh: ${video.channel_title}</small><br>
                        <small class="text-muted">Lượt xem: ${formatNumber(video.view_count)}</small><br>
                        <small class="text-muted">Lượt thích: ${formatNumber(video.like_count)}</small><br>
                        <small class="text-muted">Bình luận: ${formatNumber(video.comment_count)}</small><br>
                        <small class="text-muted">Thời lượng: ${formatDuration(video.duration)}</small>
                    </p>
                    <a href="https://www.youtube.com/watch?v=${video.video_id}" target="_blank" class="btn btn-primary btn-sm">Xem video</a>
                </div>
            </div>
        </div>
    `;
}

// Hàm cập nhật thống kê
function updateStats() {
    const totalVideos = videos.length;
    const totalViews = videos.reduce((sum, video) => sum + (parseInt(video.view_count) || 0), 0);
    const totalLikes = videos.reduce((sum, video) => sum + (parseInt(video.like_count) || 0), 0);
    const totalComments = videos.reduce((sum, video) => sum + (parseInt(video.comment_count) || 0), 0);

    document.getElementById('totalVideos').textContent = formatNumber(totalVideos);
    document.getElementById('totalViews').textContent = formatNumber(totalViews);
    document.getElementById('totalLikes').textContent = formatNumber(totalLikes);
    document.getElementById('totalComments').textContent = formatNumber(totalComments);
}

// Hàm lọc và sắp xếp video
function filterAndSortVideos() {
    const categoryFilter = document.getElementById('categoryFilter').value;
    const sortBy = document.getElementById('sortBy').value;
    const searchText = document.getElementById('searchInput').value.toLowerCase();

    let filteredVideos = videos;

    // Lọc theo danh mục
    if (categoryFilter) {
        filteredVideos = filteredVideos.filter(video => video.category_id === categoryFilter);
    }

    // Lọc theo tìm kiếm
    if (searchText) {
        filteredVideos = filteredVideos.filter(video => 
            video.title.toLowerCase().includes(searchText) ||
            video.channel_title.toLowerCase().includes(searchText)
        );
    }

    // Sắp xếp
    filteredVideos.sort((a, b) => {
        switch (sortBy) {
            case 'views':
                return (parseInt(b.view_count) || 0) - (parseInt(a.view_count) || 0);
            case 'likes':
                return (parseInt(b.like_count) || 0) - (parseInt(a.like_count) || 0);
            case 'comments':
                return (parseInt(b.comment_count) || 0) - (parseInt(a.comment_count) || 0);
            case 'published':
                return new Date(b.published_at) - new Date(a.published_at);
            default:
                return 0;
        }
    });

    return filteredVideos;
}

// Hàm hiển thị video
function displayVideos() {
    const filteredVideos = filterAndSortVideos();
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedVideos = filteredVideos.slice(startIndex, endIndex);

    const videoList = document.getElementById('videoList');
    videoList.innerHTML = paginatedVideos.map(createVideoCard).join('');

    updatePagination(filteredVideos.length);
}

// Hàm cập nhật phân trang
function updatePagination(totalItems) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const pagination = document.getElementById('pagination');
    
    let paginationHTML = '';
    
    // Nút Previous
    paginationHTML += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage - 1}">Previous</a>
        </li>
    `;
    
    // Các nút số trang
    for (let i = 1; i <= totalPages; i++) {
        if (
            i === 1 || // Trang đầu
            i === totalPages || // Trang cuối
            (i >= currentPage - 2 && i <= currentPage + 2) // Các trang xung quanh trang hiện tại
        ) {
            paginationHTML += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        } else if (
            i === currentPage - 3 ||
            i === currentPage + 3
        ) {
            paginationHTML += `
                <li class="page-item disabled">
                    <a class="page-link" href="#">...</a>
                </li>
            `;
        }
    }
    
    // Nút Next
    paginationHTML += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage + 1}">Next</a>
        </li>
    `;
    
    pagination.innerHTML = paginationHTML;
    
    // Thêm sự kiện click cho các nút phân trang
    pagination.querySelectorAll('.page-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = parseInt(e.target.dataset.page);
            if (page && page !== currentPage) {
                currentPage = page;
                displayVideos();
            }
        });
    });
}

// Hàm cập nhật danh sách danh mục
function updateCategories() {
    const categories = [...new Set(videos.map(video => video.category_id))].filter(Boolean);
    const categoryFilter = document.getElementById('categoryFilter');
    
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = `Danh mục ${category}`;
        categoryFilter.appendChild(option);
    });
}

// Hàm khởi tạo
async function init() {
    try {
        // Lấy dữ liệu từ API
        const response = await fetch('/api/videos');
        videos = await response.json();
        
        // Cập nhật giao diện
        updateStats();
        updateCategories();
        displayVideos();
        
        // Thêm sự kiện cho các nút lọc và tìm kiếm
        document.getElementById('categoryFilter').addEventListener('change', () => {
            currentPage = 1;
            displayVideos();
        });
        
        document.getElementById('sortBy').addEventListener('change', () => {
            currentPage = 1;
            displayVideos();
        });
        
        document.getElementById('searchBtn').addEventListener('click', () => {
            currentPage = 1;
            displayVideos();
        });
        
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                currentPage = 1;
                displayVideos();
            }
        });
        
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Khởi tạo khi trang đã tải xong
document.addEventListener('DOMContentLoaded', init); 