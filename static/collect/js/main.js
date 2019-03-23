var Csrf = (function () {
    return {
        init: function () {
            this._ajaxSetup();
        },
        _ajaxSetup: function () {
            var _this = this;
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!_this._csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", _this._getCookie('csrftoken'));
                    }
                }
            });
        },
        _getCookie: function (name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },
        _csrfSafeMethod: function (method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
    }
})();
var Websocket = (function () {
    var instance = new WebSocket('ws://' + window.location.host + '/comment/notification/');
    return {
        init: function () {
            this.onMessage();
        },
        onMessage: function () {
            instance.onmessage = function (json) {
                var response = JSON.parse(json.data);
                var action = response['action'];
                var data = response['data'];
                switch (action) {
                    case 'init':
                        this.connection_data = data;
                        break;
                    case 'report_created':
                        var reportObj = $('#report' + data['id']);
                        var reportLnk = reportObj.find('a');
                        var reportStatusIcon = reportObj.find('span.glyphicon');
                        reportLnk.removeClass('inactive').removeAttr('data-toggle data-original-title title');
                        reportStatusIcon.removeClass('glyphicon-remove text-danger');
                        reportStatusIcon.addClass('glyphicon-ok text-success');
                        $('.inactive[data-toggle="tooltip"]').tooltip();
                        break;
                    case 'subscribe':
                    case 'unsubscribe':
                        var commentLnk = $('.comment-subscribe-lnk');
                        commentLnk.attr('data-command', response['action']);
                        if (response['action'] === 'subscribe') {
                            commentLnk.text(commentLnk.data('subscribe_title'));
                        } else {
                            commentLnk.text(commentLnk.data('unsubscribe_title'));
                        }
                        break;
                    default:
                        if (data['sender'] !== this.connection_data['user_id']) {
                            $('#notification-popup').modal('hide');
                            $('#notification-popup .notification-text').text(data['msg']);
                            $('#notification-popup .notification-comment-body').text(data['body']);
                            $('#notification-popup').modal('show');
                        }
                }

            };
        },
        sendMessage: function (data) {
            instance.send(JSON.stringify(data));
        }
    };
})();
var CommentRepors = (function () {
    var elements = {
        form_id: 'comment-report-form',
        submit_btn_id: 'report-button',
        content_type_select_id: 'content_type',
        object_id_select_id: 'object_id',
        date_from_id: 'date_from',
        date_till_id: 'date_till',
        format_select_id: 'format',
        archive_list_id: 'report_archive',
        empty_msg_id: 'empty_reports'
    };
    return {
        init: function () {
            this._changeContentType();
            this._submitForm();
        },
        _changeContentType: function () {
            $('#' + elements.content_type_select_id).change(function () {
                var that = $(this);
                var object_id = $('#' + elements.object_id_select_id);
                if (parseInt(that.val()) === 0) {
                    object_id.html('');
                    object_id.append($('<option\>').attr('value', 0).text('----------'));
                } else {
                    $.ajax({
                        url: that.find('option:selected').data('url'),
                        method: 'POST',
                        dataType: 'json',
                        success: function (response) {
                            $.each(response['data'], function (key, val) {
                                object_id.append($('<option\>').attr('value', val.id).text(val.head));
                            });
                        }
                    });
                }
            });
        },
        _submitForm: function () {
            $('#' + elements.form_id).submit(function (e) {
                e.preventDefault();
                var that = $(this);
                var content_type = parseInt(that.find('#' + elements.content_type_select_id).val());
                var object_id = parseInt(that.find('#' + elements.object_id_select_id).val());
                if (content_type === 0) {
                    content_type = null;
                    object_id = null;
                }
                if (object_id === 0) {
                    object_id = null;
                }
                $.ajax({
                    url: that.attr('action'),
                    method: 'POST',
                    dataType: 'json',
                    data: {
                        date_from: that.find('#' + elements.date_from_id).val(),
                        date_till: that.find('#' + elements.date_till_id).val(),
                        format: that.find('#' + elements.format_select_id).val(),
                        content_type: content_type,
                        object_id: object_id,
                    },
                    success: function (response) {
                        $('#' + elements.archive_list_id + ' tbody').prepend(response['html']);
                        $('#' + elements.empty_msg_id).remove();
                        $('.inactive[data-toggle="tooltip"]').tooltip();
                    }
                });
            })
        }
    }
})();
var CommentSubscribe = (function () {
    var $this = this;
    var el = '.comment-subscribe-lnk';
    return {
        init: function () {
            this._clickMethod();
        },
        _clickMethod: function () {
            $(el).click(function (e) {
                e.preventDefault();
                var obj = $(this);
                $this.Websocket.sendMessage({
                    'command': obj.attr('data-command'),
                    'data': {
                        'content_type_id': obj.data('content_type_id'),
                        'object_id': obj.data('object_id')
                    }
                });
            });
        }
    }
})();
var Comment = (function () {
    var elements = {
        body_cls: 'comments-container-body',
        parent_hidden_inp_cls: 'comment-patent-id',
        empty_msg_cls: 'comments-empty-msg',
        create_pupup_id: 'add-comment-popup',
        create_btn_cls: 'add-comment-btn',
        create_form_cls: 'add-comment-form',
        edit_popup_id: 'edit-comment-popup',
        edit_btn_cls: 'edit-comment-btn',
        edit_form_cls: 'edit-comment-form',
        item_text_cls: 'comments-itm-txt',
        item_remove_button: 'comments-itm-rem-btn',
        item_edit_button: 'comments-itm-edt-btn',
        item_child_container_cls: 'comments-itm-children',
        item_id_pattern: 'comment',
        item_get_children_btn_cls: 'comments-itm-get-children',
        paginator_lnk_cls: 'comments-paginate-link'
    };
    return {
        init: function () {
            this._showCretePopup();
            this._createComment();
            this._editComment();
            this._showEditPopup();
            this._paginate();
            this._getChildren();
        },
        _getChildren: function () {
            $('.' + elements.body_cls).on('click', '.' + elements.item_get_children_btn_cls, function (e) {
                e.preventDefault();
                var that = $(this);
                var children_container = that.parent().parent().parent().find('.' + elements.item_child_container_cls).first();
                if (children_container.html().length == 0) {
                    $.ajax({
                        url: that.attr('href'),
                        success: function (html) {
                            children_container.html(html);
                            that.toggleClass('active');
                            children_container.toggle();
                        }
                    })
                } else {
                    that.toggleClass('active');
                    children_container.toggle();
                }
            });
        },
        _paginate: function () {
            $('.' + elements.body_cls).on('click', '.' + elements.paginator_lnk_cls, function (e) {
                e.preventDefault();
                var that = $(this);
                $.ajax({
                    url: that.attr('href'),
                    error: function (xhr, error) {
                        console.log(xhr);
                        console.log(error);
                        alert('Upss... Something wrong!');
                    },
                    success: function (html) {
                        that.remove();
                        $('.' + elements.body_cls).append(html);
                    }
                });
            })
        },
        _showCretePopup: function () {
            $('#' + elements.create_pupup_id).on('show.bs.modal', function (event) {
                var lnk = $(event.relatedTarget);
                var modal = $(this);
                modal.find('div.modal-body form input.' + elements.parent_hidden_inp_cls).val(lnk.data('parent'));
            });
        },
        _showEditPopup: function () {
            $('#' + elements.edit_popup_id).on('show.bs.modal', function (event) {
                var lnk = $(event.relatedTarget);
                var text = lnk.parent().parent().parent().find('.' + elements.item_text_cls).text();
                var modal = $(this);
                var form = $(this).find('form');
                var textarea = form.find('textarea');
                var inputHidden = form.find('input[type=hidden]');
                form.attr('action', lnk.data('action'));
                inputHidden.val(lnk.data('pk'));
                textarea.val(text);
            });
        },
        _editComment: function () {
            $('.' + elements.edit_btn_cls).click(function () {
                var form = $('.' + elements.edit_form_cls);
                var textarea = form.find('textarea');
                $.ajax({
                    method: 'POST',
                    url: form.attr('action'),
                    data: {body: textarea.val()},
                    error: function (xhr, error) {
                        console.log(xhr);
                        console.log(error);
                        alert('Upss... Something wrong!');
                    },
                    success: function (response) {
                        $('#' + elements.item_id_pattern + form.find('input[type=hidden]').val()).find('.' + elements.item_text_cls).text(textarea.val());
                        $('#' + elements.edit_popup_id).modal('hide');
                    }
                });
            });
        },
        _createComment: function () {
            $('.' + elements.create_btn_cls).click(function () {
                var form = $('.' + elements.create_form_cls);
                var textarea = form.find('textarea');
                var parent = form.find('input.' + elements.parent_hidden_inp_cls).val();
                $.ajax({
                    url: form.attr('action'),
                    method: 'post',
                    data: {
                        body: textarea.val(),
                        parent: ((parent == 0) ? null : parent)
                    },
                    dataType: 'html',
                    error: function (xhr, error) {
                        console.log(xhr);
                        console.log(error);
                        alert('Upss... Something wrong!');
                    },
                    success: function (html) {
                        if (parent == 0) {
                            var empty_msg = $('.' + elements.empty_msg_cls);
                            if (empty_msg.length > 0) {
                                empty_msg.remove();
                            }
                            $('.' + elements.body_cls).prepend(html);
                        } else {
                            $('#' + elements.item_id_pattern + parent).find('.' + elements.item_child_container_cls).first().prepend(html).show();
                        }
                        textarea.val('');
                        $('#' + elements.create_pupup_id).modal('hide');
                    }
                });
            });
        }
    }
})();
var App = (function () {
    return {
        init: function () {
            Csrf.init();
            Websocket.init();
            CommentRepors.init();
            CommentSubscribe.init();
            Comment.init();
        }
    };
})();
$(function () {
    App.init();
    $('.inactive[data-toggle="tooltip"]').tooltip();
});