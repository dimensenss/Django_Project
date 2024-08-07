$(document).ready(function ($) {
    var successMessage = $("#jq-notification");
    var notification = $('#notification');
    var warning_notification = $('#warning-jq-notification');

    if (notification.length > 0) {
        setTimeout(function () {
            notification.alert('close');

        }, 3000);
    }


    // Ловим собыитие клика по кнопке добавить в корзину
    $(document).on("click", ".add-to-cart", function (e) {
        // Блокируем его базовое действие
        e.preventDefault();

        var selectedSize = $(".form-select").val();

        // Проверяем, что цвет и размер выбраны
        if (selectedSize === '') {
            // Если не все параметры выбраны, вы можете вывести сообщение пользователю или просто вернуться
            warning_notification.html('Оберіть розмір');
            warning_notification.fadeIn(400);
            setTimeout(function () {
                warning_notification.fadeOut(400);
            }, 1500);
            return;
        }


        // Берем элемент счетчика в значке корзины и берем оттуда значение
        var goodsInCartCount = $(".goods-in-cart-count");
        var cartCount = parseInt(goodsInCartCount.first().text() || 0); // Выбираем первый элемент

        // Получаем id товара из атрибута data-product-id
        var product_id = $(this).data("product-id");
        // Из атрибута href берем ссылку на контроллер django
        var add_to_cart_url = $(this).attr("href");
        var is_order = $(this).data("is-order");


        // делаем post запрос через ajax не перезагружая страницу
        $.ajax({
            type: "POST",
            url: add_to_cart_url,
            data: {
                product_id: product_id,
                size: selectedSize,
                is_order: is_order,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                // Сообщение
                successMessage.html(data.message);
                successMessage.fadeIn(400);
                // Через 7сек убираем сообщение
                setTimeout(function () {
                    successMessage.fadeOut(400);
                }, 1500);

                // Увеличиваем количество товаров в корзине (отрисовка в шаблоне)
                cartCount++;
                goodsInCartCount.text(cartCount);

                // Меняем содержимое корзины на ответ от django (новый отрисованный фрагмент разметки корзины)
                var cartItemsContainer = $(".cart-items-container");
                cartItemsContainer.html(data.cart_items_html);

                if (is_order) {
                    var createOrderUrl = data.create_order_url;
                    window.location.href = createOrderUrl;
                }

            },

            error: function (data) {
                console.log("Ошибка при добавлении товара в корзину");
            },
        });
    });


    // Ловим собыитие клика по кнопке удалить товар из корзины
    $(document).on("click", ".remove-from-cart", function (e) {
        // Блокируем его базовое действие
        e.preventDefault();

        // Берем элемент счетчика в значке корзины и берем оттуда значение
        var goodsInCartCount = $(".goods-in-cart-count");
        var cartCount = parseInt(goodsInCartCount.first().text() || 0); // Выбираем первый элемент

        // Получаем id корзины из атрибута data-cart-id
        var cart_id = $(this).data("cart-id");
        // Из атрибута href берем ссылку на контроллер django
        var remove_from_cart = $(this).attr("href");

        // делаем post запрос через ajax не перезагружая страницу
        $.ajax({

            type: "POST",
            url: remove_from_cart,
            data: {
                cart_id: cart_id,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                // Сообщение
                successMessage.html(data.message);
                successMessage.fadeIn(400);
                // Через 7сек убираем сообщение
                setTimeout(function () {
                    successMessage.fadeOut(400);
                }, 1500);

                // Уменьшаем количество товаров в корзине (отрисовка)
                cartCount -= data.quantity_deleted;
                goodsInCartCount.text(cartCount);


                // Меняем содержимое корзины на ответ от django (новый отрисованный фрагмент разметки корзины)
                var cartItemsContainer = $(".cart-items-container");
                cartItemsContainer.html(data.cart_items_html);

            },

            error: function (data) {
                console.log("Ошибка при добавлении товара в корзину");
            },
        });
    });

    var isUpdatingCart = false; // Флаг, который указывает, идет ли в данный момент процесс обновления корзины

    function updateCart(cartID, quantity, change, url) {
        $.ajax({
            type: "POST",
            url: url,
            data: {
                cart_id: cartID,
                quantity: quantity,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },

            success: function (data) {
                // Сообщение

                // Изменяем количество товаров в корзине
                var goodsInCartCount = $(".goods-in-cart-count");
                var cartCount = parseInt(goodsInCartCount.first().text() || 0); // Выбираем первый элемент
                cartCount += change;
                goodsInCartCount.text(cartCount);

                // Меняем содержимое корзины
                var cartItemsContainer = $(".cart-items-container");
                cartItemsContainer.html(data.cart_items_html);


            },
            error: function (data) {
                console.log("Ошибка при добавлении товара в корзину");
            },
        });
    }

    $(document).on("input", ".number", function () {
        if (!isUpdatingCart) {
            isUpdatingCart = true;

            var url = $(this).closest('.input-group').find('.increment').data("cart-change-url");
            var cartID = $(this).closest('.input-group').find('.increment').data("cart-id");
            var quantity = parseInt($(this).val());

            // Проверяем, что количество находится в допустимом диапазоне
            if (quantity >= 1 && quantity <= 9999) {
                updateCart(cartID, quantity, quantity - parseInt($(this).attr('value')), url);

                // Устанавливаем задержку (при необходимости)
                setTimeout(function () {
                    isUpdatingCart = false;
                }, 200);
            } else {
                // Возвращаем предыдущее значение в случае недопустимого количества
                $(this).val(parseInt($(this).attr('value')));
                isUpdatingCart = false;
            }
        }
    });

    $(document).on("click", ".decrement", function () {
        if (!isUpdatingCart) {
            isUpdatingCart = true;

            var url = $(this).data("cart-change-url");
            var cartID = $(this).data("cart-id");
            var $input = $(this).closest('.input-group').find('.number');
            var currentValue = parseInt($input.val());

            if (currentValue > 1) {
                $input.val(currentValue - 1);
                updateCart(cartID, currentValue - 1, -1, url);
            }

            setTimeout(function () {
                isUpdatingCart = false;
            }, 200);
        }
    });

    $(document).on("click", ".increment", function () {
        if (!isUpdatingCart) {
            isUpdatingCart = true;

            var url = $(this).data("cart-change-url");
            var cartID = $(this).data("cart-id");
            var $input = $(this).closest('.input-group').find('.number');
            var currentValue = parseInt($input.val());

            $input.val(currentValue + 1);
            updateCart(cartID, currentValue + 1, 1, url);

            setTimeout(function () {
                isUpdatingCart = false;
            }, 200);
        }
    });

    $(document).on("click", ".add-to-wish-list", function (e) {
        e.preventDefault();

        var goodsInWishListCount = $(".product_in_wish_list_count");
        var wishCount = parseInt(goodsInWishListCount.first().text() || 0);

        var $this = $(this);
        var product_id = $this.data("product-id");
        var add_to_wish_list_url = $this.attr("href");

        console.log(product_id);
        console.log(add_to_wish_list_url);

        $.ajax({
            type: "GET",
            url: add_to_wish_list_url,
            data: {
                product_id: product_id,
            },
            success: function (data) {
                successMessage.html(data.message);
                successMessage.fadeIn(400);
                setTimeout(function () {
                    successMessage.fadeOut(400);
                }, 1500);

                wishCount = data.change_value + wishCount;
                goodsInWishListCount.text(wishCount);

                var WishListContainer = $(".wish-list-container");
                if (WishListContainer.length > 0) {
                    WishListContainer.html(data.wish_list_container);
                }

                // Обновляем класс иконки сердца и текст, если параграф существует
                var wishIcon = $this.find('.wish-icon');
                var parentParagraph = $this.closest('p.product-base-info');
                if (parentParagraph.length > 0) {
                    if (wishIcon.hasClass('fa-regular')) {
                        wishIcon.removeClass('fa-regular fa-heart').addClass('fa-solid fa-heart');
                        parentParagraph.contents().filter(function () {
                            return this.nodeType === 3; // Узел текста
                        }).first().replaceWith('Видалити з бажаного ');
                    } else {
                        wishIcon.removeClass('fa-solid fa-heart').addClass('fa-regular fa-heart');
                        parentParagraph.contents().filter(function () {
                            return this.nodeType === 3; // Узел текста
                        }).first().replaceWith('Додати в бажання &nbsp; ');
                    }
                } else {
                    // Только переключаем иконку сердца, если параграфа нет
                    if (wishIcon.hasClass('fa-regular')) {
                        wishIcon.removeClass('fa-regular fa-heart').addClass('fa-solid fa-heart');
                    } else {
                        wishIcon.removeClass('fa-solid fa-heart').addClass('fa-regular fa-heart');
                    }
                }
            },

            error: function (data) {
                console.log("Ошибка при добавлении в список желаний");
            },
        });
    });


    $("input[name='requires_delivery']").change(function () {
        var selectedValue = $(this).val();
        // Скрываем или отображаем input ввода адреса доставки
        if (selectedValue === "1") {
            $("#deliveryAddressField").show();
        } else {
            $("#deliveryAddressField").hide();
        }
    });


    $('.image-popup-vertical-fit').magnificPopup({
        type: 'image',
        closeOnContentClick: true,
        mainClass: 'mfp-img-mobile',
        image: {
            verticalFit: true
        }

    });

    $('.image-popup-fit-width').magnificPopup({
        type: 'image',
        closeOnContentClick: true,
        image: {
            verticalFit: false
        }
    });

    $('.image-popup-no-margins').magnificPopup({
        type: 'image',
        closeOnContentClick: true,
        closeBtnInside: false,
        fixedContentPos: true,
        mainClass: 'mfp-no-margins mfp-with-zoom', // class to remove default margin from left and right side
        image: {
            verticalFit: true
        },
        zoom: {
            enabled: true,
            duration: 300 // don't foget to change the duration also in CSS
        }
    });

    'use strict';

    var togglers = document.getElementsByClassName("caret");
    var i;

    for (i = 0; i < togglers.length; i++) {
        togglers[i].addEventListener("mouseover", function () {
            this.parentElement.querySelector(".nested").classList.add("active");
            this.classList.add("caret-down");
        });

        togglers[i].addEventListener("mouseout", function () {
            this.parentElement.querySelector(".nested").classList.remove("active");
            this.classList.remove("caret-down");
        });
    }


    // $(document).ready(function () {
    //         $('#password_reset_form').submit(function (e) {
    //             e.preventDefault(); // предотвращаем обычную отправку формы
    //             $.ajax({
    //                 type: $(this).attr('method'),
    //                 url: $(this).attr('action'),
    //                 data: $(this).serialize(),
    //                 success: function (data) {
    //                     successMessage.html(data.message);
    //                     successMessage.fadeIn(400);
    //                     // Через 7сек убираем сообщение
    //                     setTimeout(function () {
    //                         successMessage.fadeOut(400);
    //                     }, 1500);
    //
    //
    //
    //                     $('#message-container').html(data.info_message);
    //                 },
    //                 error: function (data) {
    //                     // Обработка ошибок при отправке формы
    //                     // В data.responseText содержится текст ошибки
    //                     alert('Произошла ошибка: ' + data.responseText);
    //                 }
    //             });
    //         });
    //     });
    // Форматирования ввода номера телефона в форме (xxx) xxx-хххx
    document.getElementById('id_phone_number').addEventListener('input', function (e) {
        var x = e.target.value.replace(/\D/g, '').match(/(\d{0,3})(\d{0,3})(\d{0,4})/);
        e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
    });

    // Проверяем на стороне клинта коррекность номера телефона в форме xxx-xxx-хх-хx
    $('#create_order_form').on('submit', function (event) {
        var phoneNumber = $('#id_phone_number').val();
        var regex = /^\(\d{3}\) \d{3}-\d{4}$/;

        if (!regex.test(phoneNumber)) {
            $('#phone_number_error').show();
            event.preventDefault();
        } else {
            $('#phone_number_error').hide();

            // Очистка номера телефона от скобок и тире перед отправкой формы
            var cleanedPhoneNumber = phoneNumber.replace(/[()\-\s]/g, '');
            $('#id_phone_number').val(cleanedPhoneNumber);
        }
    });


});

function displayFileName() {
    var fileInput = document.getElementById('file');
    var fileNameDisplay = document.getElementById('fileName');

    if (fileInput.files.length > 0) {
        fileNameDisplay.textContent = fileInput.files[0].name;
    } else {
        fileNameDisplay.textContent = '';
    }
}

$(document).ready(function () {
    $('#id_tags').magicSuggest({
        // Настраивайте конфигурацию по мере необходимости
        placeholder: 'Введіть теги',
        name: 'tags',
        // Другие параметры
    });
});


document.addEventListener('DOMContentLoaded', function () {
    var checkboxes = document.querySelectorAll('.size-checkbox');
    var selectedSizesInput = document.getElementById('id_size');

    checkboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            updateSelectedSizes();
        });
    });

    // При загрузке страницы восстанавливаем выбранные чекбоксы
    restoreSelectedSizes();

    function updateSelectedSizes() {
        var selectedSizes = Array.from(checkboxes)
            .filter(function (checkbox) {
                return checkbox.checked;
            })
            .map(function (checkbox) {
                return checkbox.value;
            })
            .join(' ');

        selectedSizesInput.value = selectedSizes;

        // Сохраняем выбранные чекбоксы в localStorage
        saveSelectedSizes(selectedSizes);
    }

    function saveSelectedSizes(selectedSizes) {
        localStorage.setItem('selectedSizes', selectedSizes);
    }

    function restoreSelectedSizes() {
        var savedSelectedSizes = localStorage.getItem('selectedSizes');
        if (savedSelectedSizes) {
            var savedSizesArray = savedSelectedSizes.split(' ');

            checkboxes.forEach(function (checkbox) {
                checkbox.checked = savedSizesArray.includes(checkbox.value);
            });

            updateSelectedSizes(); // Обновляем инпут после восстановления чекбоксов
        }
    }
});

document.addEventListener('DOMContentLoaded', function () {
    var checkboxes = document.querySelectorAll('.sm-size-checkbox');

    var selectedSizesInput = document.getElementById('id_sizes');

    checkboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            updateSelectedSizes();
        });
    });

    // При загрузке страницы восстанавливаем выбранные чекбоксы
    restoreSelectedSizes();

    function updateSelectedSizes() {
        var selectedSizes = Array.from(checkboxes)
            .filter(function (checkbox) {
                return checkbox.checked;
            })
            .map(function (checkbox) {
                return checkbox.value;
            })
            .join(' ');

        selectedSizesInput.value = selectedSizes;

        // Сохраняем выбранные чекбоксы в localStorage
        saveSelectedSizes(selectedSizes);
    }

    function saveSelectedSizes(selectedSizes) {
        localStorage.setItem('selectedSizes', selectedSizes);
    }

    function restoreSelectedSizes() {
        var savedSelectedSizes = localStorage.getItem('selectedSizes');
        if (savedSelectedSizes) {
            var savedSizesArray = savedSelectedSizes.split(' ');

            checkboxes.forEach(function (checkbox) {
                checkbox.checked = savedSizesArray.includes(checkbox.value);
            });

            updateSelectedSizes(); // Обновляем инпут после восстановления чекбоксов
        }
    }
});

$(document).ready(function () {
    var btnTable = $("#btnSizesTable");
    var sizesTable = $("#sizesTable");
    var btnAdditionalContent = $("#btnAdditionalContent");
    var additionalContent = $("#additionalContent");

    if (btnTable.length && sizesTable.length) {
        btnTable.on("click", function () {
            // Show the "Information" tab
            $("#nav-information-tab").tab('show');
            // Wait for the tab to be fully shown, then scroll
            $('#nav-information-tab').on('shown.bs.tab', function (e) {
                scrollToElement(sizesTable);
            });
        });
    }

    if (btnAdditionalContent.length && additionalContent.length) {
        btnAdditionalContent.on("click", function () {
            // Show the "Additional information" tab
            $("#nav-additional-info-tab").tab('show');
            // Wait for the tab to be fully shown, then scroll
            $('#nav-additional-info-tab').on('shown.bs.tab', function (e) {
                scrollToElement(additionalContent);
            });
        });
    }

    function scrollToElement(element) {
        var targetOffset = element.offset().top;
        var navbarHeight = $('.navbar').outerHeight() || 0;
        $('html, body').animate({
            scrollTop: targetOffset - navbarHeight
        }, 600);
    }
});
document.addEventListener("DOMContentLoaded", function () {
    var loaderWrapper = document.getElementById("loader-wrapper");
    if (loaderWrapper) {
        loaderWrapper.style.display = "none";
    }
});


$(document).ready(function () {
    var priceMinInputLg = document.getElementById("id_price__gte");
    var priceMaxInputLg = document.getElementById("id_price__lte");
    var priceMinInputSm = document.getElementById("id_price__gte_sm");
    var priceMaxInputSm = document.getElementById("id_price__lte_sm");

    if (priceMinInputLg && priceMaxInputLg && priceMinInputSm && priceMaxInputSm) {
        priceMinInputSm.value = parseInt(priceMinInputLg.value);
        priceMaxInputSm.value = parseInt(priceMaxInputLg.value);

        initializeSlider("slider-range-sm", priceMinInputSm, priceMaxInputSm);
        initializeSlider("slider-range-lg", priceMinInputLg, priceMaxInputLg);
    } else {
        return;
    }


    function initializeSlider(sliderId, priceMinInput, priceMaxInput) {
        var priceRange = document.getElementById(sliderId);
        var min_price = parseInt($(priceRange).data("min-price"));
        var max_price = parseInt($(priceRange).data("max-price"));

        if (isNaN(parseInt(priceMinInput.value)) && isNaN(parseInt(priceMinInput.value))) {
            priceMinInput.value = min_price;
            priceMaxInput.value = max_price;
        }

        if (parseInt(priceMinInput.value) > parseInt(priceMaxInput.value) || parseInt(priceMinInput.value) < 0) {
            priceMinInput.value = min_price;
            priceMaxInput.value = max_price;
        }

        $("#" + sliderId).slider({
            range: true,
            min: min_price,
            max: max_price,
            values: [parseInt(priceMinInput.value), parseInt(priceMaxInput.value)],
            slide: function (event, ui) {
                priceMinInput.value = ui.values[0];
                priceMaxInput.value = ui.values[1];
            }
        });
    }
});
