Ext._define('edocs.protocolo.box.HistoryGrid', {
    extend: 'edocs.protocolo.box.Grid',

    mixins: {
        '1': 'edocs.protocolo.filters.FilterMixin'
    },

    __boxAction: 'outbox',

    simpleTitle: 'Histórico',

    toolbarConfig: ['actions', '-', 'search', '->', '-', 'filter'],

    __undoSend: function(pkset) {
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Desfazendo o envio dos protocolos...'});

        mask.show();
        Ext.Ajax.request({
            url: core.callAction('EDOCManage', 'undo_send'),
            params: {
                pkset: pkset
            },
            scope: this,
            callback: function() {
                mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success) {
                    this.getStore().reload();
                    if(this.mainBox) this.mainBox().getStore().reload();
                    if(this.pesonBox) this.pesonBox().getStore().reload();
                }
                else
                    Ext.Msg.show({
                        title: 'Desfazendo o envio dos protocolos',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Desfazendo o envio dos protocolos',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    __undoSendSpecific: function(pkset) {
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Desfazendo o envio do protocolo...'});

        mask.show();
        Ext.Ajax.request({
            url: core.callAction('EDOCManage', 'undo_send_specific'),
            params: {
                pkset: pkset
            },
            scope: this,
            callback: function() {
                mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success) {
                    this.getStore().reload();
                    if(this.mainBox) this.mainBox().getStore().reload();
                    if(this.pesonBox) this.pesonBox().getStore().reload();
                }
                else
                    Ext.Msg.show({
                        title: 'Desfazendo o envio do protocolo',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Desfazendo o envio do protocolo',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    undoSend: function() {
        var selection = this.getSelectionModel().getSelections().filter(
          function(data) {
            return !data.get('with_workflow');
          }
        );

        if(selection.length > 0)
            Ext.Msg.show({
                title: 'Desfazer o envio',
                msg: 'Tem certeza que deseja desfazer o envio dos protocolos selecionados?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn == 'no') return;

                    this.__undoSend(
                        selection.map(
                            function(data) {
                                return data.get('pk');
                            }
                        )
                    );
                }
            });
        else
            Ext.Msg.show({
                title: 'Desfazer o envio',
                msg: 'Primeiro selecione os protocolos que deseja desfazer o envio.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    undoSendSpecific: function() {
        var selection = this.getSelectionModel().getSelections().filter(
          function(data) {
            return !data.get('with_workflow');
          }
        );;

        if(selection.length > 0)
            Ext.Msg.show({
                title: 'Desfazer o envio do item selecionado',
                msg: 'Tem certeza que deseja desfazer o envio para '+selection[0].get('send_to_unicode')+' ?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn == 'no') return;

                    this.__undoSendSpecific(selection[0].get('pk'));
                }
            });
        else
            Ext.Msg.show({
                title: 'Desfazer o envio do item selecionado',
                msg: 'Primeiro selecione os protocolo que deseja desfazer o envio.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    getActionsToolbarItem: function(cfg) {
        if(!this._actionsToolbarItem)
            this._actionsToolbarItem = Ext._create('Ext.Button', {
                iconCls: 'icon-edocs icon-protocolo-actions',
                text: 'Ações',
                menu: this.getActionsMenuItems()
            });

        return this._actionsToolbarItem;
    },

    getActionsMenuItems: function(contextOnly) {
        var menu = [];

        contextOnly = core.nullValue(contextOnly, false);

        if(!contextOnly)
            Ext.emptyFn();

        if(menu.length > 0) menu.push('-');

        menu = menu.concat([
            {
                text: 'Desfazer/desfinalizar envio',
                iconCls: 'icon-edocs icon-protocolo-undo-icon',
                scope: this,
                handler: this.undoSend
            },
            '-',
            {
                text: 'Desfazer/desfinalizar este envio',
                iconCls: 'icon-edocs icon-protocolo-undo-icon',
                scope: this,
                handler: this.undoSendSpecific
            },
            '-',
            {
                text: 'Imprimir recibo',
                iconCls: 'icon-edocs icon-protocolo-report',
                scope: this,
                handler: this.reportQuitter
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

        if(this.generalProtocol)
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

    selectDepartment: function() {
        Ext._create('edocs.protocolo.filters.DepartmentWindow', {
            grid: this,
            nameField: 'lotacao_origem',
            filterProperties: this.getFilterBoxDepartment()
        }).show();
    },

    getFilterBoxDepartment: function() {
        return [{property: 'lotacao_origem', stage: 100}];
    },

    getFilterMenu: function(cfg) {
        if(!this._filterMenu) {
            this._filterMenu = [
                this.senderFilter(),
                this.interestedFilter(),
                this.originFilter(),
                this.destinationFilter(),
                this.sendDateFilter(),
                this.specieFilter(),
                '-',
                this.notReceivedFilter(),
                this.urgentFilter(),
                this.confidentialFilter(),
                this.electronicFilter(),
                this.physicalFilter(),
                '-',
                {
                    text: 'Desfazer todos os filtros',
                    scope: this,
                    hideOnClick: false,
                    handler: function() {
                        this.removeSenderFilter();
                        this.removeInterestedFilter();
                        this.removeOriginFilter();
                        this.removeDestinationFilter();
                        this.removeSendDateFilter();
                        this.removeSpecieFilter();
                        this.removeNotReceivedFilter();
                        this.removeUrgentFilter();
                        this.removeConfidentialFilter();
                        this.removeElectronicFilter();
                        this.removeFilterProperty('lotacao_origem', 100);

                        this.notReceivedFilter().setChecked(false);
                        this.urgentFilter().setChecked(false);
                        this.confidentialFilter().setChecked(false);
                        this.electronicFilter().setChecked(false);
                        this.physicalFilter().setChecked(false);

                        this.getStore().reload();
                        this.updateItemToolbar();
                    }
                }
            ];
        }

        return this._filterMenu;
    },

    getRowContextMenu: function(cfg) {
        if(!this._rowContextMenu)
            this._rowContextMenu = Ext._create('Ext.menu.Menu', {
                items: this.getActionsMenuItems(true)
            });

        return this._rowContextMenu;
    },

    __rendererItem: function(value, cell, data) {
        var tpl = new Ext.XTemplate(
            '<div class="edoc-row">',
                '<div class="edoc-iconset">',
                    core.rendererIconGrid(data.get('icons')),
                '</div>',
                '<div class="edoc-item">',
                    '<div>',
                        '<div class="subject inline-with-crop" ext:qtip="Assunto">{subject}</div>',
                    '</div>',
                    '<div>',
                        '<div class="subject inline-with-crop" ext:qtip="Interessado">{interested_unicode}</div>',
                    '</div>',
                    '<div class="two-column">',
                        '<tpl if="seal_number">',
                            '<div class="one" ext:qtip="Protocolo - Chancela">{code} - {seal_number}</div>',
                        '</tpl>',
                        '<tpl if="!seal_number">',
                            '<div class="one" ext:qtip="Protocolo">{code}</div>',
                        '</tpl>',
                        '<div class="two" ext:qtip="Data de envio">{send_date}</div>',
                    '</div>',
                    '<div class="two-column">',
                        '<div class="one" ext:qtip="Enviado para">{send_to_unicode}</div>',
                        '<div class="two" ext:qtip="Enviado por">{from_person}</div>',
                    '</div>',
                '</div>',
            '</div>'
        );

        return tpl.apply(data.data);
    },


    generateFlowchart: function () {
        var selected = this.getSelectionModel().getSelected();

        if (selected) {
            edocs.reports.Flowchart.generate({
                el: this.getEl(),
                waitMessage: 'Gerando fluxograma...',
                params: {
                    protocol: selected.get('protocol'),
                    output_format: 'pdf'
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Fluxograma',
                msg: 'Selecione o protocolo para o qual deseja gerar o fluxograma.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    constructor: function(cfg) {
        this.generalProtocol = (cfg.generalProtocol !== undefined ? cfg.generalProtocol : false);

        Ext.applyIf(
            cfg,
            {
                generalProtocol: false,
                store: this.factoryStore(false),
            }
        );

        edocs.protocolo.box.HistoryGrid.superclass.constructor.call(this, cfg);

        this.on({
            scope: this,
            rowcontextmenu: function(me, index, evt) {
                this.getRowContextMenu().showAt(evt.getXY());
                evt.stopEvent();
            }
        });
    }
});
