document.addEventListener('DOMContentLoaded', function() {
    // メニュートグル機能
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // メニュー項目がクリックされたらメニューを閉じる（モバイル用）
        const navItems = document.querySelectorAll('.nav-link');
        navItems.forEach(function(item) {
            item.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    navbarCollapse.classList.remove('show');
                }
            });
        });
    }
    
    // スクロール時のヘッダー固定とコンテンツのパディング調整
    const header = document.querySelector('header');
    const main = document.querySelector('main');
    
    // パディング調整関数
    function adjustLayout() {
        if (window.scrollY > 50) {
            header.classList.add('fixed-header');
            if (main) {
                const headerHeight = header.offsetHeight;
                main.style.paddingTop = headerHeight + 'px';
                document.body.style.paddingTop = '0';
            }
        } else {
            header.classList.remove('fixed-header');
            if (main) {
                main.style.paddingTop = '0';
                document.body.style.paddingTop = '0';
            }
        }
    }
    
    if (header) {
        // 初期ロード時の調整
        adjustLayout();
        
        // スクロール時の調整
        window.addEventListener('scroll', adjustLayout);
        
        // リサイズ時の調整
        window.addEventListener('resize', adjustLayout);
    }
    
    // ウィンドウサイズが変更された時、モバイルからデスクトップへの変更時の処理
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            // デスクトップサイズになった時、メニューを表示
            if (navbarCollapse) {
                navbarCollapse.classList.remove('show');
            }
        }
    });
}); 