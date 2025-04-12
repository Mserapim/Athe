Ext._define('rh.teletrabalho.teletrabalho_competencia.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.teletrabalho.teletrabalho_competencia.Restful',

    width: 550,
    height: 470,

    constructor: function(cfg) {
        rh.teletrabalho.teletrabalho_competencia.Window.superclass.constructor.call(this, cfg);
    },

    getPanelInformationItems: function(cfg_window){
        var items = rh.teletrabalho.teletrabalho_competencia.Window.superclass.getPanelInformationItems.call(this, cfg_window);
        
        return items;
    },
   
});