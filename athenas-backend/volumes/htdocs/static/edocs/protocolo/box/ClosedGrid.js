/**
 *
 **/

Ext._define('edocs.protocolo.box.ClosedGrid', {
    extend: 'edocs.protocolo.box.Grid',

    mixins: {
        '1': 'edocs.protocolo.filters.FilterMixin'
    },

    __boxAction: 'closedbox',

    simpleTitle: 'Finalizado',

    toolbarConfig: ['actions', '-', 'search', '->', '-', 'filter'],

    __signReceived: function(pkset) {
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Recebendo protocolos...'});

        mask.show();
        Ext.Ajax.request({
            url: core.callAction('EDOCManage', 'sign_receive_closed'),
            params: {
                pkset: pkset
            },
            scope: this,
            callback: function() {
                mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success)
                    this.getStore().reload();
                else
                    Ext.Msg.show({
                        title: 'Recebendo protocolos',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Recebendo protocolos',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    __undoClose: function(pkset) {
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Desfazendo finalização dos protocolos...'});

        mask.show();
        Ext.Ajax.request({
            url: core.callAction('EDOCManage', 'undo_close'),
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
                        title: 'Desfazendo finalização dos protocolos',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Desfazendo finalização dos protocolos',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    undoClose: function() {
        var selection = this.getSelectionModel().getSelections().filter(
          function(data) {
            return !data.get('with_workflow');
          }
        );;

        if(selection.length > 0)
            Ext.Msg.show({
                title: 'Desfazer finalização protocolo',
                msg: 'Tem certeza que deseja desfazer finalização dos protocolos selecionados?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn == 'no') return;

                    this.__undoClose(
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
                title: 'Desfazer finalização protocolo',
                msg: 'Primeiro selecione os protocolos que deseja o envio.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    getActionsMenuItems: function(contextOnly) {
        var menu = [];

        contextOnly = core.nullValue(contextOnly, false);

        menu = menu.concat([
            {
                text: 'Desfazer finalização',
                iconCls: 'icon-edocs icon-protocolo-reopen',
                scope: this,
                handler: this.undoClose
            },
            '-',
            {
                text: 'Receber selecionados',
                iconCls: 'icon-edocs icon-protocolo-read',
                scope: this,
                handler: this.signReceived
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

    getActionsToolbarItem: function(cfg) {
        if(!this._actionsToolbarItem)
            this._actionsToolbarItem = Ext._create('Ext.Button', {
                iconCls: 'icon-edocs icon-protocolo-actions',
                text: 'Ações',
                menu: this.getActionsMenuItems()
            });

        return this._actionsToolbarItem;
    },

    getRowContextMenu: function(cfg) {
        if(!this._rowContextMenu)
            this._rowContextMenu = Ext._create('Ext.menu.Menu', {
                items: this.getActionsMenuItems(true)
            });

        return this._rowContextMenu;
    },

    getFilterBoxDepartment: function() {
        return [{property: 'lotacao_destino', stage: 100}];
    },

    getFilterMenu: function(cfg) {
        if(!this._filterMenu) {
            this._filterMenu = [
                this.interestedFilter(),
                this.originFilter(),
                this.destinationFilter(),
                this.sendDateFilter(),
                this.specieFilter(),
                '-',
                this.notReceivedFilter(),
                this.confidentialFilter(),
                this.electronicFilter(),
                this.physicalFilter(),
                '-',
                {
                    text: 'Desfazer todos os filtros',
                    scope: this,
                    hideOnClick: false,
                    handler: function() {
                        this.removeInterestedFilter();
                        this.removeOriginFilter();
                        this.removeDestinationFilter();
                        this.removeSendDateFilter();
                        this.removeSpecieFilter();
                        this.removeNotReceivedFilter();
                        this.removeConfidentialFilter();
                        this.removeElectronicFilter();
                        this.removeFilterProperty('lotacao_destino', 100, false);

                        this.notReceivedFilter().setChecked(false);
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
        cfg = core.nullValue(cfg, {});
        this.generalProtocol = (cfg.generalProtocol !== undefined ? cfg.generalProtocol : false);

        Ext.applyIf(
            cfg,
            {
                generalProtocol: false
            }
        );

        edocs.protocolo.box.ClosedGrid.superclass.constructor.call(this, cfg);

        this.on({
            scope: this,
            rowcontextmenu: function(me, index, evt) {
                if(this.getSelectionModel().getSelections().length === 0)
                    this.getSelectionModel().selectRow(index);

                this.getRowContextMenu().showAt(evt.getXY());
                evt.stopEvent();
            }
        });
    }

});
