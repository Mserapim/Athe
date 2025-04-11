Ext._define('raf.adjustment.BaseGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'raf.adjustment.BaseWindow',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'accept', 'requestInformation', 'answerInformation', 'cancelAdjustment', 'rejected', 'undoAction', 'searchprocessnumber', '->', '-'],

    openSearchProcessNumber: function() {
        Ext._create('raf.searchprocessnumber.SearchProcessNumberWindow', {
            modal: false,
            values: { }
        }).show();
    },

    getSearchProcessNumberAction: function() {
        if(!this._searchProcessNumberAction){
            this._searchProcessNumberAction = new Ext.Button({
                xtype: 'button',
                text: 'Pesquisar por número',
                iconCls: 'icon-core icon-core-select',
                scope: this,
                handler: function() { this.openSearchProcessNumber(); }
            });
        }
        return this._searchProcessNumberAction;
    },

    getCancelAdjustmentAction: function() {
        if(!this._cancelAdjustmentAction){
            this._cancelAdjustmentAction = new Ext.Button({
                xtype: 'button',
                text: 'Cancelar Solicitação',
                iconCls: 'icon-core icon-core-delete',
                scope: this,
                handler: function() {
                    var selected = this.getSelectionModel().getSelected();
                    if(selected) {
                        if ([1, 2, 3, 4, 6].indexOf(selected.data.situation) >= 0) {
                            Ext.Msg.show({
                                title: 'Cancelar solicitação',
                                msg: 'Cancelamento só possível para solicitações nos estados "NÃO ENVIADO" e "NÃO AVALIADO"',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        } else {
                            Ext.Msg.show({
                                title: 'Cancelar solicitação',
                                icon: Ext.Msg.QUESTION,
                                buttons: Ext.Msg.YESNO,
                                msg: 'Tem certeza que deseja cancelar a solicitação selecionada?',
                                scope: this,
                                fn: function(btn) {
                                    if(btn == 'no') return;
                                    this.cancel(selected);
                                }
                            });
                        }
                    }
                    else
                        this.alertError({title: 'Cancelar', message: 'Selecione a solicitação que deseja cancelar.'});
                }
            });
        }
        return this._cancelAdjustmentAction;
    },

    cancel: function(value) {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Cancelando solicitação...'});
        mask.show();
        rest.action(
            {
                adjustment_list: value.get('pk'),
                answer: 'Cancelado pelo usuário',
                situation: 4
            },
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        core.invokeCallback((this.callback || {}).success);
                        this.getStore().load({});
                        this.fireEvent('updatedItemGrid', value);
                        Ext.Msg.show({
                            title: 'Cancelar solicitação de ajuste',
                            msg: rst.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                    }
                    else
                        Ext.Msg.show({
                            title: 'Cancelar solicitação de ajuste',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Cancelar solicitação de ajuste',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    alertError: function(wcfg) {
        Ext.Msg.show({
            title: wcfg.title,
            msg: wcfg.message,
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        });
    },

    createItem: function(record) {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Criando nova Solcitação de Ajustes...'});
        mask.show();
        rest.save(
            {
                activity: this.params.activity,
                workerlocation: this.params.workerlocation,
                // quiz: this.params.quiz,
                item: this.params.item,
                subitem: this.params.subitem,
            },
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        core.invokeCallback((this.callback || {}).success);
                        this.setFilterProperty('activity', rst.activity_id, 1000, true);
                        this.getStore().load({
                            'scope': this,
                            'callback': function() {
                                this.getSelectionModel().selectLastRow();
                                this.updateItem();
                                this.params.gridMain.getStore().reload();
                            }
                        });
                    }
                    else
                        Ext.Msg.show({
                            title: 'Criar Solicitação de Ajustes',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Criar Solicitação de Ajustes',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    updateItem: function(record) {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            if (this.getSelectionModel().getSelections().length == 1){
                this.params.adjustment = selected.data.pk;
                this.params.activity = selected.data.activity;
                // this.params.quiz = this.selected.data.quiz;
                this.params.situation = selected.data.situation;
                raf.adjustment.BaseGrid.superclass.updateItem.call(this, record);
            }
            else {
                this.alertError({title: 'Solicitar mais informações', message: 'Selecione apenas um item para solicitar mais informações.'});
            }
        }
        else
            this.alertError({title: 'Solicitar mais informações', message: 'Selecione um item para solicitar mais informações.'});
    },

    getAcceptAction: function() {
        if(!this._acceptAction){
            this._acceptAction = new Ext.Button({
                xtype: 'button',
                text: 'Aceitar',
                iconCls: 'icon-core icon-core-success',
                scope: this,
                handler: function() {
                    var selection = this.getSelectionModel().getSelections();
                    if(selection) {
                        Ext.Msg.show({
                            title: 'Deferir solicitação',
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            msg: 'Tem certeza que deseja aceitar a solicitação selecionada?',
                            scope: this,
                            fn: function(btn) {
                                if(btn == 'no') return;
                                this.accept(selection.map(
                                        function(data) {
                                            return data.get('pk');
                                        }
                                    ).toString());
                            }
                        });
                    } else {
                        this.alertError({title: 'Aceitar', message: 'Selecione um item para aceitá-lo.'});
                    }
                }
            });
        }
        return this._acceptAction;
    },

    accept: function(value) {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Realizando ajuste...'});
        mask.show();
        rest.action(
            {
                adjustment_list: value,
                answer: 'Deferido conforme a solicitação',
                situation: 2
            },
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        core.invokeCallback((this.callback || {}).success);
                        this.getStore().load({});
                        Ext.Msg.show({
                            title: 'Aceitar pedido de ajuste',
                            msg: rst.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                    }
                    else
                        Ext.Msg.show({
                            title: 'Aceitar pedido de ajuste',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Aceitar pedido de ajuste',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    getRejectedAction: function() {
        if(!this._rejectedAction){
            this._rejectedAction = new Ext.Button({
                xtype: 'button',
                text: 'Rejeitar',
                iconCls: 'icon-core icon-core-error',
                scope: this,
                handler: function() {
                    var selection = this.getSelectionModel().getSelections();
                    if(selection) {
                        this.reject(selection.map(
                                function(data) {
                                    return data.get('pk');
                                }
                            ).toString());
                    }
                    else
                        this.alertError({title: 'Rejeitar', message: 'Selecione um item para rejeita-lo.'});
                }
            });
        }
        return this._rejectedAction;
    },

    reject: function(value) {
        Ext._create('raf.adjustment.RejectAdjustmentWindow', {
            modal: true,
            values: {
                adjustment_list: value,
                situation: 3,
            },
            callback: {
                success: {
                    scope: this,
                    fn: function(instance) {
                        core.invokeCallback((this.callback || {}).success);
                        this.getStore().load({});
                    }
                }
            }
        }).show();
    },

    getUndoAction: function() {
        if(!this._undoAction){
            this._undoAction = new Ext.Button({
                xtype: 'button',
                text: 'Desfazer decisão',
                iconCls: 'icon-core icon-core-remove-selected',
                scope: this,
                // disabled: true,
                handler: function() {
                    var selection = this.getSelectionModel().getSelections();
                    if(selection) {
                        // this.undoAction(selected);
                        this.undoAction(selection.map(
                                function(data) {
                                    return data.get('pk');
                                }
                            ).toString());
                    }
                    else
                        this.alertError({title: 'Desfazer', message: 'Selecione um item para desfazer decisão.'});
                }
            });
        }
        return this._undoAction;
    },

    undoAction: function(value) {
      Ext._create('raf.adjustment.UndoActionAdjustmentWindow', {
          modal: true,
          values: {
            //   adjustment: value.get('pk'),
              adjustment_list: value,
            //   activity_unicode : value.get('activity_unicode')
          },
          callback: {
              success: {
                  scope: this,
                  fn: function(instance) {
                      core.invokeCallback((this.callback || {}).success);
                      this.getStore().load({});
                  }
              }
          }
      }).show();
    },

    getRequestInformationAction: function() {
        if(!this._requestInformationAction){
            this._requestInformationAction = new Ext.Button({
                xtype: 'button',
                text: 'Solicitar mais informações',
                iconCls: 'icon-core icon-core-report-edit',
                scope: this,
                handler: function() {
                    var selected = this.getSelectionModel().getSelected();
                    if(selected) {
                        if (this.getSelectionModel().getSelections().length == 1){
                            this.openAdjustmentCommunicationWindow(selected);
                        }
                        else {
                            this.alertError({title: 'Solicitar mais informações', message: 'Selecione apenas um item para solicitar mais informações.'});
                        }
                    }
                    else
                        this.alertError({title: 'Solicitar mais informações', message: 'Selecione um item para solicitar mais informações.'});
                }
            });
        }
        return this._requestInformationAction;
    },

    openAdjustmentCommunicationForAdminWindow: function(value) {
        Ext._create('raf.conversation.AnswerWindow', {
            modal: true,
            values: {
                conversation: value.get('conversation'),
            },
            callback: {
                success: {
                    scope: this,
                    fn: function(instance) {
                        core.invokeCallback((this.callback || {}).success);
                        this.getStore().load({});
                    }
                }
            }
        }).show();
    },

    getAnswerInformationAction: function() {
        if(!this._answerInformationAction){
            this._answerInformationAction = new Ext.Button({
                xtype: 'button',
                text: 'Responder',
                iconCls: 'icon-core icon-core-report-edit',
                scope: this,
                handler: function() {
                    var selected = this.getSelectionModel().getSelected();
                    if(selected)
                        if ([2, 3, 4, 6].indexOf(selected.data.situation) >= 0) {
                            Ext.Msg.show({
                                title: 'Responder solicitação',
                                msg: 'Não é possível responder solicitações já encerradas',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        } else {
                            this.openAdjustmentCommunicationWindow(selected);
                        }
                    else
                        this.alertError({title: 'Responder', message: 'Selecione o item que deseja responder.'});
                }
            });
        }
        return this._answerInformationAction;
    },

    openAdjustmentCommunicationWindow: function(value) {
        Ext._create('raf.conversation.AnswerWindow', {
            modal: true,
            values: {
                conversation: value.get('conversation'),
                origin: value.get('location'),
                situation: 0,
            },
            callback: {
                success: {
                    scope: this,
                    fn: function(instance) {
                        core.invokeCallback((this.callback || {}).success);
                        this.getStore().load({});
                    }
                }
            }
        }).show();
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 26, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Atividade', dataIndex: 'unicode', id: 'autoExpandColumn', menuDisabled: true},
                    {header: 'Solicitação', dataIndex: 'activity_created_at', width: 120, menuDisabled: true,},
                    {header: 'status', dataIndex: 'status', width: 100, hidden: true, menuDisabled: true},
                    {header: 'Quantidade', dataIndex: 'amount', width: 60, hidden: true, menuDisabled: true},
                ]
            );

        return this._columnModel;
    },

    adjustment: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(value !== undefined) {
            this._adjustment = value;
            if(dispatch) this.observerAdjustment();
        }
        return this._adjustment;
    },

    observerAdjustment: function() {
        var value = this.adjustment();
        if(value) {
            this.readView(value);
        }
        else {
            this.detailView.disable();
            this.detailView.setPageContent('');
        }
    },

    readView: function(adjustment) {
        var mask = new Ext.LoadMask(this.detailView.getEl(), {msg: 'Carregado informações...'});
        var rest = this.factoryRestful();
        mask.show();
        this.detailView.enable();
        this.detailView.setPageContent('');
        Ext.Ajax.request({
            url: core.callAction(rest.resource, 'renderer_document'),
            scope: this,
            autoAbort: true,
            params: {
                adjustment: adjustment
            },
            callback: function() {
                mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                var me = this;
                if(rst.success) {
                    this.detailView.setPageContent(rst.content);
                }
                else
                    Ext.Msg.show({
                        title: 'Carregando informações',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
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
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                colorized: false
            }
        );
        Ext.apply(
            cfg,
            {
                showFinished: true,
                viewConfig: {
                    getRowClass: function(record, rowIndex, rp, ds){
                        if(cfg.colorized && record.get('conversation_in_box'))
                            return 'x-grid3-green-simple';
                    }
                }
            }
        );
        raf.adjustment.BaseGrid.superclass.constructor.call(this, cfg);
        if((this.detailView)) {
            this.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selection = sel.getSelections();
                    if(selection.length > 0){
                        this.adjustment(selection[0].get('pk'));
                    } else {
                        this.adjustment(null);
                    }
                }
            });
            this.getStore().on({
                scope: this,
                load: function() {
                    this.observerAdjustment();
                },
            });
        }
    }
});

core.RestfulGrid.register(
    'raf.adjustment.BaseRestful',
    'raf.adjustment.BaseGrid'
);
