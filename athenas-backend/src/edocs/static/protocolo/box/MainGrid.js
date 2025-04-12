/**
 *
 **/

Ext._define('edocs.protocolo.box.MainGrid', {
    extend: 'edocs.protocolo.box.Grid',

    mixins: {
        '1': 'edocs.protocolo.filters.FilterMixin'
    },

    __boxAction: 'inbox',

    simpleTitle: 'Principal',

    toolbarConfig: ['actions', '-', 'forms', '-', 'search', '->', 'filter'],

    statics: {
        registerSpecialType: function (opts) {
            var db = (edocs.protocolo.box.MainGrid._specialTypesDB || []);
            db.push(opts);
            edocs.protocolo.box.MainGrid._specialTypesDB = db;
        },

        haveSpecialType: function () {
            return ((edocs.protocolo.box.MainGrid._specialTypesDB || []).length > 0);
        },

        updateSpecialItem: function (pk, specialType, self) {
            var windowRestful = null;
            var db = (edocs.protocolo.box.MainGrid._specialTypesDB || []);

            db.forEach(
                function (item) {
                    if (item.specialType === specialType) {
                        windowRestful = item.restWindow;
                    }
                }
            );

            if (windowRestful) {
                var WindowRestful = eval(windowRestful);
                var resource = WindowRestful.prototype._resource;
                self.__updateProtocol(pk, resource, WindowRestful);
            } else {
                console.error(
                    'Não foi possivel determinar a Window de edição para o tipo especial ' + specialType + '.'
                );
            }
        },

        specialTypes: function (self) {
            return (edocs.protocolo.box.MainGrid._specialTypesDB || [])
                .map(function (item) {
                    return {
                        text: item.title,
                        iconCls: item.iconCls,
                        scope: self,
                        group: item.group,
                        handler: function () {
                            Ext._create(item.restWindow, {
                                modal: true,
                                success: {
                                    scope: self,
                                    fn: function () {
                                        this.getStore().reload();
                                        if (this.otherInboxFn) this.otherInboxFn().getStore().reload();
                                    }
                                }
                            }).show();
                        }
                    }
                });
        }
    },
    __signReceived: function (pkset) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Recebendo protocolos...' });

        mask.show();
        Ext.Ajax.request({
            url: core.callAction('EDOCManage', 'sign_received'),
            params: {
                pkset: pkset
            },
            scope: this,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var result = Ext.decode(xhr.responseText);

                if (result.personal) {
                    /*
                        SE FOR ENVIADO PARA PESSOAL E NAO POSSUI LOCAL DE TRABALHO INFORMADO NA REQUISICAO,
                        SOLICITAR VIA WINDOW O PREENCHIMENTO
                    */
                    var wnd = Ext._create('edocs.protocolo.SelectLocationWindow', {
                        modal: true,
                        resource: this,
                        params: {
                            'pkset': pkset,
                        },
                        callback: {
                            success: {
                                scope: this,
                                fn: function () {
                                    this.getStore().reload();
                                }
                            }
                        }
                    });

                    wnd.show()

                } else {
                    // ENVIO PARA DEPARTAMENTO
                    if (result.success) {
                        this.getStore().reload();
                        if (this.otherInboxFn) this.otherInboxFn().getStore().reload();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Recebendo protocolos',
                            msg: result.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });

                }

            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Recebendo protocolos',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    __signDocuments: function (pkset) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Assinando documentos...' });

        mask.show();
        Ext.Ajax.request({
            url: core.callAction('EDOCManage', 'sign_document'),
            params: {
                pkset: pkset
            },
            scope: this,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var rst = Ext.decode(xhr.responseText);

                if (rst.success) {
                    this.getStore().reload();
                    if (this.otherInboxFn) this.otherInboxFn().getStore().reload();
                }
                else
                    Ext.Msg.show({
                        title: 'Assinando documentos',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Assinando documentos',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    signDocument: function () {
        var selection = this.getSelectionModel().getSelections().filter(
            function (data) {
                return !data.get('with_workflow');
            }
        );

        if (selection.length > 0)
            Ext.Msg.show({
                title: 'Assinando documentos',
                msg: 'Tem certeza que deseja assinar os documentos selecionados?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function (btn) {
                    if (btn == 'no') return;

                    this.__signDocuments(selection.map(function (data) {
                        return data.get('pk');
                    }));
                }
            });
        else
            Ext.Msg.show({
                title: 'Assinando documentos',
                msg: 'Primeiro selecione os documentos que deseja assinar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    getFilterBoxDepartment: function () {
        return [{ property: 'lotacao_destino', stage: 100 }];
    },

    getFilterMenu: function (cfg) {
        if (!this._filterMenu) {
            this._filterMenu = [
                this.interestedFilter(),
                this.originFilter(),
                this.sendDateFilter(),
                this.specieFilter(),
                '-',
                this.notReceivedFilter(),
                this.urgentFilter(),
                this.confidentialFilter(),
                this.electronicFilter(),
                this.physicalFilter(),
                this.withWorkflowFilter(),
                '-',
                {
                    text: 'Desfazer todos os filtros',
                    scope: this,
                    hideOnClick: false,
                    handler: function () {
                        this.removeInterestedFilter();
                        this.removeOriginFilter();
                        this.removeSendDateFilter();
                        this.removeSpecieFilter();
                        this.removeNotReceivedFilter();
                        this.removeUrgentFilter();
                        this.removeConfidentialFilter();
                        this.removeElectronicFilter();
                        this.removeFilterProperty('lotacao_destino', 100, false);

                        this.notReceivedFilter().setChecked(false);
                        this.physicalFilter().setChecked(false);
                        this.electronicFilter().setChecked(false);
                        this.urgentFilter().setChecked(false);
                        this.withWorkflowFilter().setChecked(false);

                        this.getStore().reload();
                        this.updateItemToolbar();
                    }
                }
            ];
        }

        return this._filterMenu;
    },

    __signUnReceived: function (pkset) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Desfazendo o recebimento dos protocolos...' });

        mask.show();
        Ext.Ajax.request({
            url: core.callAction('EDOCManage', 'sign_unreceived'),
            params: {
                pkset: pkset
            },
            scope: this,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var rst = Ext.decode(xhr.responseText);

                if (rst.success) {
                    this.getStore().reload();
                    if (this.otherInboxFn) this.otherInboxFn().getStore().reload();
                }
                else
                    Ext.Msg.show({
                        title: 'Desfazendo o recebimento dos protocolos',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Desfazendo o recebimento dos protocolos',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    __closeProtocol: function (pkset) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Finalizando protocolos...' });

        mask.show();
        Ext.Ajax.request({
            url: core.callAction('EDOCManage', 'close_protocol'),
            params: {
                pkset: pkset
            },
            scope: this,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var rst = Ext.decode(xhr.responseText);

                if (rst.success) {
                    this.getStore().reload();
                    if (this.historyBox) this.historyBox.getStore().reload();
                    if (this.otherInboxFn) this.otherInboxFn().getStore().reload();
                }
                else
                    Ext.Msg.show({
                        title: 'Finalizando Protocolos',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Finalizando Protocolos',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    closeProtocol: function () {
        var selection = this.getSelectionModel().getSelections().filter(
            function (data) {
                return !data.get('with_workflow');
            }
        );

        if (selection.length > 0) {

            var flag = false;

            Ext.each(
                selection,
                function (data) {
                    if (!data.get('is_read')) {
                        flag = true;
                        return false;
                    }
                }
            );

            if (flag)
                Ext.Msg.show({
                    title: 'Finalizando protocolos',
                    msg: 'Existem protocolos que ainda não foram recebidos. Deve receber-los primeiro antes de tentar finalizar',
                    icon: Ext.Msg.WARNING,
                    buttons: Ext.Msg.OK
                });
            else
                Ext._create('edocs.protocolo.box.ComposeFinalizeWindow', {
                    movement: selection.map(function (data) { return data.get('pk'); }),
                    success: {
                        scope: this,
                        fn: function (rst) {
                            this.getStore().reload();
                            if (this.otherInboxFn) this.otherInboxFn().getStore().reload();
                            if (this.historyBox) this.historyBox.getStore().reload();
                        }
                    }
                }).show();
        } else
            Ext.Msg.show({
                title: 'Finalizando protocolos',
                msg: 'Primeiro selecione os protocolos que deseja finalizar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    // _TODEL_ Funcionalidade não utilizada.
    signUnReceived: function () {
        var selection = this.getSelectionModel().getSelections().filter(
            function (data) {
                return !data.get('with_workflow');
            }
        );

        if (selection.length > 0)
            Ext.Msg.show({
                title: 'Desfazendo o recebimento de protocolos',
                msg: 'Tem certeza que deseja desfazer o recebimento dos protocolos selecionados?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function (btn) {
                    if (btn == 'no') return;

                    this.__signUnReceived(selection.map(function (data) {
                        return data.get('pk');
                    }));
                }
            });
        else
            Ext.Msg.show({
                title: 'Desfazendo o recebimento de protocolos',
                msg: 'Primeiro selecione os protocolos que deseja desfazer o recebimento.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    compositeClass: function () {
        return (this.generalProtocol ? 'edocs.protocolo.box.ComposeExWindow' : 'edocs.protocolo.box.ComposeWindow');
    },

    createProtocol: function () {
        Ext._create(this.compositeClass(), {
            modal: true,
            action: 'create',
            success: {
                scope: this,
                fn: function () {
                    this.getStore().reload();
                    if (this.otherInboxFn) this.otherInboxFn().getStore().reload();
                }
            }
        }).show();
    },

    __updateProtocol: function (pk, resource, WindowClass) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Editando protocolo...' });

        resource = (resource ? resource : 'EDOCManage');
        WindowClass = (WindowClass ? WindowClass : this.compositeClass());

        mask.show();
        Ext.Ajax.request({
            url: core.callAction(resource, 'read_movement'),
            params: { pk: pk },
            scope: this,
            callback: function () { mask.hide(); },
            success: function (xhr) {
                var result = Ext.decode(xhr.responseText);

                if (result.success) {
                    Ext._create(WindowClass, {
                        modal: true,
                        action: 'update',
                        objectId: pk,
                        values: result.instance,
                        success: {
                            scope: this,
                            fn: function () {
                                this.getStore().reload();
                                if (this.otherInboxFn) this.otherInboxFn().getStore().reload();
                            }
                        }
                    }).show();
                }
                else
                    Ext.Msg.show({
                        title: 'Editando protocolo',
                        msg: result.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Editando protocolo',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    __updateProtocolWithSpecialType: function (pk, specialType) {
        edocs.protocolo.box.MainGrid.updateSpecialItem(
            pk,
            specialType,
            this
        );
    },

    __removeProtocol: function (pkset) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Removendo protocolo...' });

        mask.show();
        Ext.Ajax.request({
            url: core.callAction('EDOCManage', 'undocketing'),
            params: { pkset: pkset },
            scope: this,
            callback: function () { mask.hide(); },
            success: function (xhr) {
                var rst = Ext.decode(xhr.responseText);

                if (rst.success) {
                    this.getStore().reload();
                    if (this.otherInboxFn) this.otherInboxFn().getStore().reload();
                }
                else
                    Ext.Msg.show({
                        title: 'Removendo protocolo',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Removendo protocolo',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    updateProtocol: function () {
        var selection = this.getSelectionModel().getSelected();

        if (selection && selection.get('step') === 0) {
            if (selection.get('special_type')) {
                this.__updateProtocolWithSpecialType(
                    selection.get('pk'),
                    selection.get('special_type')
                );
            } else {
                this.__updateProtocol(selection.get('pk'));
            }
        }
        else if (selection && selection.get('step') > 0)
            Ext.Msg.show({
                title: 'Editar protocolo',
                msg: 'Não posso editar um protocolo que já foi movimentado.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        else
            Ext.Msg.show({
                title: 'Editar protocolo',
                msg: 'Primeiro selecione um protocolo para ser editado.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    removeProtocol: function () {
        var selection = this.getSelectionModel().getSelections().filter(
            function (data) {
                return !data.get('with_workflow');
            }
        );

        if (selection)
            Ext.Msg.show({
                title: 'Removendo protocolos',
                msg: 'Tem certeza que deseja remover os protocolos selecionados?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function (btn) {
                    if (btn == 'no') return;
                    this.__removeProtocol(selection.map(function (data) { return data.get('pk'); }));
                }
            });
        else
            Ext.Msg.show({
                title: 'Removendo protocolo',
                msg: 'Primeiro selecione um protocolo para ser removido.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    unreadExists: function (selections) {
        var result = false;

        Ext.each(selections, function (data) {
            if (!data.get('is_read')) {
                result = true;
                return false;
            }
        });

        return result;
    },

    hasMovementDistinctConfidentiality: function (selections) {
        var first = selections[0].get('confidential');

        for (var i = 0; i < selections.length; i++) {
            if (selections[i].get('confidential') !== first)
                return true;
        }

        return false;
    },

    moveProtocols: function () {
        var selections = this.getSelectionModel().getSelections().filter(
            function (data) {
                return !data.get('with_workflow');
            }
        );

        if (selections.length > 0) {
            if (this.unreadExists(selections))
                Ext.Msg.show({
                    title: 'Movimentando itens',
                    msg: 'Existem protocolos que ainda não foram recebidos. Receba-os primeiro antes de tentar movimenta-los',
                    icon: Ext.Msg.WARNING,
                    buttons: Ext.Msg.OK
                });
            else if (this.hasMovementDistinctConfidentiality(selections))
                Ext.Msg.show({
                    title: 'Movimentando itens',
                    msg: 'Não é possível movimentar protocolos com sigilosidades distintas.',
                    icon: Ext.Msg.WARNING,
                    buttons: Ext.Msg.OK
                });
            else
                Ext.Msg.show({
                    title: 'Movimentar itens',
                    msg: 'Tem certeza que deseja movimentar os itens selecionados?',
                    icon: Ext.Msg.QUESTION,
                    buttons: Ext.Msg.YESNO,
                    scope: this,
                    fn: function (btn) {
                        if (btn == 'no') return;

                        Ext._create('edocs.protocolo.box.ComposeMovementWindow', {
                            movement: selections.map(function (data) { return data.get('pk'); }),
                            control: selections[0].get('control'),
                            controlType: selections[0].get('control_type'),
                            legalPrerogative: selections[0].get('legal_prerogative'),
                            isCommitted: selections[0].get('is_committed'),
                            isSecret: selections[0].get('is_secret'),
                            success: {
                                scope: this,
                                fn: function (rst) {
                                    this.getStore().reload();
                                    if (this.otherInboxFn) this.otherInboxFn().getStore().reload();
                                    if (this.historyBox) this.historyBox.getStore().reload();
                                }
                            }
                        }).show();
                    }
                });
        }
        else
            Ext.Msg.show({
                title: 'Removendo protocolo',
                msg: 'Primeiro selecione um protocolo para ser removido.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    createAssessmentNoticeOffice: function() {
        var selections = this.getSelectionModel().getSelections().filter(
            function (data) {
                return !data.get('with_workflow');
            }
        );

        if (selections.length > 0) {
            Ext._create('judicial.parts.AssessmentNoticeOfficeWindow', {
                action: 'create',
                params: {
                    location: selections[0].get('send_to'),
                    protocol_origin: selections[0].get('protocol')
                },
                values: {
                    notice_title: selections[0].get('subject'),
                    notice: selections[0].get('content'),
                    interested: selections[0].get('interested'),
                },
                callback: {
                    success: {
                        scope: this,
                        fn: function(instance) {
                            core.invokeCallback(this.success || {fn: Ext.emptyFn}, instance);
                            this.close();
                        }
                    }
                },
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Criando o procedimento',
                msg: 'Primeiro selecione e/ou receba o protocolo que deseja importar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
        });
    },

    showAllowedListWindow: function() {
        var selected = this.getSelectionModel().getSelected();

        Ext._create('common.document_access.allowedlistitem.Modal', {
            title: 'Credenciais de acesso',
            control: selected.data.control,
            gridConfig: {
                allowUpdate: false,
                allowRemove: false,
                columnAction: false,
            }
        }).show();
    },

    sendDiary: function (pksend) {
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Carregando informações...'});

        var selected = this.getSelectionModel().getSelected();

        mask.show();

        if (selected && selected.get('is_read')){
            Ext.Ajax.request({
                url: core.callAction('JournalDocument', 'save_info_edoc'),
                scope: this,
                autoAbort: true,
                params: {
                    pk: selected.get('protocol')
                },
                scope: this,
                callback: function() {
                    mask.hide();
                },
                success: function(xhr) {
                    var result = Ext.decode(xhr.responseText);

                    if(result.success){
                        // console.log('Sucesso');
                        Ext.Msg.show({
                            'title': 'Carregando informações!',
                            'msg': result.message,
                            'icon': Ext.Msg.OK,
                            'buttons': Ext.Msg.OK
                        });
                    }else{
                        Ext.Msg.show({
                            'title': 'Carregando informações!',
                            'msg': result.message,
                            'icon': Ext.Msg.ERROR,
                            'buttons': Ext.Msg.OK
                        });
                    }
                },
                failure: function() {
                    Ext.Msg.show({
                        title: 'Carregando informações',
                        msg: 'Recurso indisponivel no momento.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            });
        }else{
            mask.hide();
            Ext.Msg.show({
                title: 'Atenção',
                msg: 'Para enviar ao diário oficial é necessário selecionar o documento e recebê-lo.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getActionsMenuItems: function (contextOnly) {
        var menu = [];

        contextOnly = core.nullValue(contextOnly, false);

        if (!contextOnly) {
            menu = menu.concat([
                {
                    text: 'Novo',
                    iconCls: 'icon-core icon-core-add',
                    scope: this,
                    handler: this.createProtocol
                },
                {
                    text: 'Editar',
                    iconCls: 'icon-core icon-core-edit',
                    scope: this,
                    handler: this.updateProtocol
                },
                {
                    text: 'Excluir',
                    iconCls: 'icon-core icon-core-delete',
                    scope: this,
                    handler: this.removeProtocol
                }
            ]);
        }

        if (menu.length > 0) menu.push('-');

        menu = menu.concat([
            {
                text: 'Receber selecionados',
                iconCls: 'icon-edocs icon-protocolo-read',
                scope: this,
                handler: this.signReceived
            },
            '-',
            {
                text: 'Credenciais de acesso',
                iconCls: 'icon-document_access icon-document_access-allowedlist',
                scope: this,
                handler: this.showAllowedListWindow
            },
            '-',
            {
                text: 'Movimentar protocolos',
                iconCls: 'icon-edocs icon-protocolo-moviment',
                scope: this,
                handler: this.moveProtocols
            },
            {
                text: 'Finalizar protocolo',
                iconCls: 'icon-edocs icon-protocolo-close-protocol',
                scope: this,
                handler: this.closeProtocol
            },

            {
                text: 'Assinar documento',
                iconCls: 'icon-edocs icon-protocolo-sign-document',
                scope: this,
                handler: this.signDocument
            },
            '-',
            {
                text: 'Criar um procedimento',
                iconCls: 'icon-judicial icon-ejud-protocol',
                scope: this,
                handler: this.createAssessmentNoticeOffice
            },
            '-',
            {
                text: 'Imprimir protocolo conforme visualização',
                iconCls: 'icon-edocs icon-protocolo-report',
                scope: this,
                handler: this.reportProtocolRenderer
            },
            {
                text: 'Visualizar fluxograma do protocolo',
                iconCls: 'icon-edocs icon-protocolo-flowchart',
                scope: this,
                handler: this.generateFlowchart
            }
        ]);

        if (menu.length > 0) menu.push('-');

        if (this.generalProtocol)
            menu = menu.concat([
                {
                    text: 'Imprimir etiqueta',
                    iconCls: 'icon-edocs icon-protocolo-report',
                    scope: this,
                    handler: this.reportLabel
                }
            ]);

        return menu;
    },

    getActionsToolbarItem: function (cfg) {
        if (!this._actionsToolbarItem)
            this._actionsToolbarItem = Ext._create('Ext.Button', {
                iconCls: 'icon-edocs icon-protocolo-actions',
                text: 'Ações',
                menu: this.getActionsMenuItems()
            });

        return this._actionsToolbarItem;
    },

    groupFormsMenu: function () {
        const groupBy = (arr, key) => {
            const initialValue = {};
            return arr.reduce((acc, cval) => {
                    const myAttribute = cval[key];
                    if (typeof myAttribute === 'undefined') { acc['Outros'] = [...(acc[myAttribute] || []), cval]; }
                    else { acc[myAttribute] = [...(acc[myAttribute] || []), cval] }
                    return acc;
            }, initialValue);
        };

        var menus = edocs.protocolo.box.MainGrid.specialTypes(this)
        var groups = groupBy(menus, 'group')
        return Object.keys(groups).map(function(group){
            return {
                text: group,
                iconCls: '',
                menu: [groups[group].map(function (item){ return item }) ]
            }
        })
    },

    getFormsToolbarItem: function (cfg) {
        if (!this._formsToolbarItem)
            this._formsToolbarItem = Ext._create('Ext.Button', {
                text: 'Formulários',
                iconCls: 'icon-core icon-core-reports',
                scope: this,
                menu: this.groupFormsMenu()
            });

        return this._formsToolbarItem;
    },

    getRowContextMenu: function (cfg) {
        if (!this._rowContextMenu)
            this._rowContextMenu = Ext._create('Ext.menu.Menu', {
                items: this.getActionsMenuItems(true)
            });

        return this._rowContextMenu;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        this.generalProtocol = (cfg.generalProtocol !== undefined ? cfg.generalProtocol : false);

        Ext.applyIf(
            cfg,
            {
                generalProtocol: false,
                store: this.factoryStore(),
            }
        );

        cfg.preFilter = (cfg.preFilter || []);
        cfg.preFilter.push({
            property: 'with_workflow',
            value: 'off',
            stage: 101
        });

        edocs.protocolo.box.MainGrid.superclass.constructor.call(this, cfg);

        this.on({
            scope: this,
            rowcontextmenu: function (me, index, evt) {
                if (this.getSelectionModel().getSelections().length === 0)
                    this.getSelectionModel().selectRow(index);

                this.getRowContextMenu().showAt(evt.getXY());
                evt.stopEvent();
            },
            rowdblclick: function (me, index) {
                var data;

                if (index >= 0) {
                    data = me.getStore().getAt(index);

                    if (data.get('with_workflow')) {
                        Ext.Msg.show({
                            title: 'Operação negada',
                            icon: Ext.Msg.ERROR,
                            msg: 'Como este protocolo é de movimentação controlada ele não pode ser manipulado por aqui.',
                            buttons: Ext.Msg.OK
                        });

                        return;
                    }

                    if (!data.get('is_read'))
                        me.signReceived();
                    else if (data.get('step') === 0)
                        me.updateProtocol();
                    else
                        me.moveProtocols();
                }
            }
        });
    }
});
