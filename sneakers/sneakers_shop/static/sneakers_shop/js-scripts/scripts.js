$(document).ready(function () {
        // Активация главной карусели
        $('#mainCarousel').carousel();

        // Обработка наведения на миниатюры
        $('#carousel-thumbs .thumbnail').on('click', function () {
            var slideIndex = $(this).data('bs-slide-to');
            $('#mainCarousel').carousel(slideIndex);
        });
    });