/**
 * Created by lemki on 15.11.17.
 */

$(document).ready(function () {
    $('#btn-count-buy').bind('click', function () {
            var buyCount = $('#buy_count').val();
            var buyPrice = $('#buy_price').val();
            if ($.isNumeric(buyCount) && $.isNumeric(buyPrice)){
                var buyTotal = buyCount * buyPrice;
                $('#buy_total').show();
                $('#btn-buy').prop('disabled', false);
                $('#buy_total_text').text(buyTotal.toFixed(6))
            }
            else {
                $('#buy_total').hide();
                $('#btn-buy').prop('disabled', true);
            }
        }
    );
    $('#btn-count-sell').bind('click', function () {
            var sellCount = $('#sell_count').val();
            var sellPrice = $('#sell_price').val();
            if ($.isNumeric(sellCount) && $.isNumeric(sellPrice)){
                var sellTotal = sellCount * sellPrice;
                $('#sell_total').show();
                $('#btn-sell').prop('disabled', false);
                $('#sell_total_text').text(sellTotal.toFixed(6))
            }
            else {
                $('#sell_total').hide();
                $('#btn-sell').prop('disabled', true);
            }
        }
    );
});