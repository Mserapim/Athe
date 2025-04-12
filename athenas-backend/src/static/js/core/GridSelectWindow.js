/**
 *
 **/
Ext._define('core.GridSelectWindow', {
    'extend': 'core.GridActionWindow',

    'doSelect': function() {
        var selected;

        if(this.multi)
            selected = this.getGridPanel().getSelectionModel().getSelections();
        else
            selected = this.getGridPanel().getSelectionModel().getSelected();

        core.invokeCallback(this.callback, selected);
        this.destroy();
    },

    'getActionButton': function() {
        if(!this._actionButton)
            this._actionButton = Ext._create('Ext.Button', {
                'text': 'Selecionar',
                'scope': this,
                'handler': this.doSelect
            });

        return this._actionButton;
    },

    'getGridPanel': function(cfg) {
        var hwnd = this;

        if(!this._gridPanel)
            if(cfg.restGrid) {
                this._gridPanel = Ext._create(cfg.restGrid, {
                    'region': 'center',
                    'disableNode': cfg.selected ? cfg.selected.id : undefined,
                    'doubleClickHandler': function() {
                        hwnd.doSelect();
                    }
                });
            }
            else if(cfg.rest) {
                this._gridPanel = core.RestfulGrid.factoryGrid(
                    cfg.rest,
                    {
                        'region': 'center',
                        'doubleClickHandler': function() {
                            hwnd.doSelect();
                        }
                    }
                )
            }
            else
                throw 'BUG: Defina um restGrid ou um rest parametro na configuração do Objeto.'

        return this._gridPanel;
    }
});
