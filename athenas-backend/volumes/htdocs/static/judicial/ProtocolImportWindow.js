/*
 *
 */
Ext._define('judicial.ProtocolImportWindow', {
    extend: 'Ext.Window',

    getInboxPanel: function(cfg) {
        if(!this._inboxPanel) {
            this._inboxPanel = Ext._create('edocs.protocolo.box.MainGrid', {
                region: 'center',
                detailView: this.getTilePanel(cfg),
                gridAutoLoad: false
            });

            this._inboxPanel.getDepartmentToolbarItem().disable();
            this._inboxPanel.getDepartmentToolbarItem().hide();
            this._inboxPanel.setFilterProperty('lotacao_destino', cfg.params.location, 2, false);
            this._inboxPanel.setFilterProperty('destinatario', null, 10000);
        }

        return this._inboxPanel;
    },

    getTilePanel: function(cfg) {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                region: 'east',
                split: true,
                width: 850,
                minWidth: 850
            });

        return this._tilePanel;
    },

    importProtocol: function() {
        var selected = this.getInboxPanel().getSelectionModel().getSelected();

        if(selected && !selected.get('with_workflow')) {
            Ext._create('judicial.parts.AssessmentNoticeOfficeWindow', {
                action: 'create',
                params: {
                    location: this.params.location,
                    protocol_origin: selected.get('protocol')
                },
                values: {
                    notice_title: selected.get('subject'),
                    notice: selected.get('content'),
                    interested: selected.get('interested')
                },
                callback: {
                    success: {
                        scope: this,
                        fn: function(instance) {
                            core.invokeCallback(this.success || {fn: Ext.emptyFn}, instance);
                            this.close();
                        }
                    }
                }
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Importando protocolo',
                msg: 'Primeiro selecione o protocolo que deseja importar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Criar procedimento',
                    scope: this,
                    handler: function() {
                        var selected = this.getInboxPanel().getSelectionModel().getSelected();
                        if(selected && selected.data.is_read) {
                            this.importProtocol();
                        }
                        else
                            Ext.Msg.show({
                                title: 'Importando protocolo',
                                msg: 'Primeiro selecione e/ou receba o protocolo que deseja importar.',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                    }
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ];

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Importar do Protocolo',
                modal: true,
                width: Ext.getBody().getBox().width * 0.9,
                height: Ext.getBody().getBox().height * 0.9
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                buttons: this.getButtons(),
                items: [
                    this.getInboxPanel(cfg),
                    this.getTilePanel(cfg)
                ]
            }
        );

        judicial.ProtocolImportWindow.superclass.constructor.call(this, cfg);
    }
});
