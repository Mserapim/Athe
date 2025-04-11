Ext._define('planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerManageAdmin', {
    
    extend: 'planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerManage',

    getMinuteSolicitationManagerGrid: function () {
        if (!this._minuteSolicitationManagerGrid) {
            var me = this;
            this._minuteSolicitationManagerGrid = Ext._create('planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerGridAdmin', {
                region: 'center',
            });

            this._minuteSolicitationManagerGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function (selm) {
                    var selection = selm.getSelections();
                    if (selection.length > 0) {
                        this.solicitation(selection[0].id);
                    } else {
                        this.solicitation(null);
                    }
                }
            });

            this._minuteSolicitationManagerGrid.getStore().on({
                scope: this,
                load: function () {
                    this.observeSolicitation();
                }
            });
        }

        return this._minuteSolicitationManagerGrid;
    },
});