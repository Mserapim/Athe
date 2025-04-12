/**
 *
 **/
Ext._define('judicial.tac.ActivityHistoryRestfulWindow', {
    extend: 'Ext.Window',

    getGrid: function(){
        var box = Ext.getBody().getBox();
        if (!this._grid){
            this._grid = Ext._create('judicial.tac.ActivityHistoryGrid', {
                region: 'center',
                border: false,
                height: box.height * 0.4,
            });
        }

        var cm = this._grid.getColumnModel();
        cm.setHidden(1, true);
        cm.setHidden(8, true);

        return this._grid;
    },

    _aplicationRevision: function(){
        var selected = this.getGrid().getSelectionModel().getSelected();
        var rest = Ext._create('judicial.tac.ActivityHistoryRestful', {});
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Aplicando alterações...'});

        mask.show();
        rest.doRequest(
            rest.getRoute('apply_history', false, 'POST', {
                params: {
                    pk: selected.get('pk')
                },
                scope: this,
                callback: function() {
                    mask.hide();
                    mask = null;
                },
                success: function(xhr) {
                    this.getGrid().getStore().reload();
                    this.callback.call(this.scope ? this.scope : window);
                },
                failure: function(xhr) {
                    Ext.Msg.show({
                        title: 'Erro',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Não consegui aplicar a alteração'
                    });
                }
            })
        );
    },

    getPanel: function() {
        if(!this._controPanel)
            this._controPanel = Ext._create('Ext.Panel', {
                items: [
                    this.getGrid()
                ]
            });

        return this._controPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Histórico de Mudanças',
            }
        );
        var box = Ext.getBody().getBox();
        Ext.apply(
            cfg,
            {
                items: [
                    this.getPanel()
                ],
                width: box.width*0.5,
                height: box.height*0.5,
                modal:true,
            }
        );

        this._activityId = cfg.activityId
        this.getGrid().setFilterProperty('activity', this._activityId);
        this.getGrid().setParam('activity', this._activityId);

        var tbar = this.getGrid().getToolbar();
        tbar.remove(tbar.getComponent(0));
        tbar.remove(tbar.getComponent(0));
        tbar.remove(tbar.getComponent(0));
        tbar.remove(tbar.getComponent(0));

        judicial.tac.ActivityHistoryRestfulWindow.superclass.constructor.call(this, cfg);
    }
});
