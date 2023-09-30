
$(document).ready(function(){
    $('.slider').slick({
        dots: true, // Опционально: добавьте точки для навигации
        infinite: true,
        speed: 300,
        slidesToShow: 1,
        adaptiveHeight: true, // Адаптивная высота для слайдов
        prevArrow: '<button class="slick-prev">Previous</button>', // Кнопка "Предыдущий слайд"
        nextArrow: '<button class="slick-next">Next</button>', // Кнопка "Следующий слайд"
    });
});

