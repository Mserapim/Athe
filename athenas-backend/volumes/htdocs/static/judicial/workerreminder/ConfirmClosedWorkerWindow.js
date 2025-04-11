Ext._define('judicial.workerreminder.ConfirmClosedWorderwindow', {
    extend: 'Ext.Window',

    getSelectedsGrid: function(cfg) {
        var selections = cfg.params.selections
        return {
            title: 'Procedimentos selecionados',
            layout:'table',
            defaults: {
                // applied to each contained panel
                bodyStyle:'padding:100px',
                style: { width: '100%' }
            },
            layoutConfig: {
                // The total column count must be specified here
                columns: 3
            },
            items: selections.map(function(data) {
                return {
                        xtype: 'box',
                        html: '=> '+ data['lawsuit'] + ': ' + data['description'],
                        height: 20,
                        padding:5,
                        colspan: 3,
                    }
            })
        }
    },

    getMainPanel: function(cfg) {
        if(!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel', {
                minHeight: 200,
                items : [
                    this.getSelectedsGrid(cfg)
                ]
            });

        return this._mainPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: false,
                items: [
                    this.getMainPanel(cfg),
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Concluir análises selecionadas',
            border: false
        });

        Ext.apply(cfg, {
            width: 900,
            items: [
                this.getFormPanel(cfg)
            ],
            buttons: [
                {
                    text: 'Concluir',
                    scope: this,
                    handler: function() {
                        var rest = cfg.params.rest
                        var storage = cfg.params.storage

                        rest.resolve(
                            cfg.params.selections.map(function (data){ return data.id }),
                            {
                                scope: this,
                                fn: function(rst) {
                                    core.invokeCallback((this.callback || {}).success);
                                    storage.reload();
                                }
                            },
                            {
                                scope: this,
                                fn: function(message) {
                                    Ext.Msg.show({
                                        title: 'Concluído',
                                        msg: message,
                                        icon: Ext.Msg.INFO,
                                        buttons: Ext.Msg.ERROR
                                    });
                                }
                            },
                            {
                                scope: this,
                                fn: function() {
                                    this.close();
                                }
                            }
                        )
                    }
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });

       judicial.workerreminder.ConfirmClosedWorderwindow.superclass.constructor.call(this, cfg);
    }
});
